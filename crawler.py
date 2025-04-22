import requests
from bs4 import BeautifulSoup
import json
import csv
import os
import random
import re
import time
import logging
import argparse
from collections import defaultdict, Counter
from urllib.parse import urljoin, urlparse, parse_qs
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crawler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Define user agents for rotation
USER_AGENTS = [
    # Windows browsers
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.55",
    
    # macOS browsers
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_5_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_5_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
    
    # Linux browsers
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    
    # Mobile browsers
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/92.0.4515.90 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36"
]

class RateLimiter:
    """Smart rate limiter with domain-specific delays and user agent rotation"""
    
    def __init__(self, initial_requests_per_second=2, rotate_agent_after=10):
        self.initial_delay = 1.0 / initial_requests_per_second
        self.delays = defaultdict(lambda: self.initial_delay)
        self.last_request_time = defaultdict(float)
        self.rotate_agent_after = rotate_agent_after
        self.request_count = 0
        self.user_agents = USER_AGENTS.copy()
        random.shuffle(self.user_agents)
        self.current_agent_index = 0
        self.start_time = time.time()
    
    def wait(self, domain):
        """Wait appropriate time for domain"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time[domain]
        delay = self.delays[domain]
        
        if elapsed < delay:
            time.sleep(delay - elapsed)
        
        self.last_request_time[domain] = time.time()
    
    def handle_429(self, domain):
        """Handle rate limiting (HTTP 429)"""
        # Exponential backoff
        self.delays[domain] *= 2
        return self.delays[domain]
    
    def handle_success(self, domain):
        """Handle successful request"""
        # Gradually reduce delay on success, but not below initial
        self.delays[domain] = max(self.initial_delay, self.delays[domain] * 0.95)
    
    def get_next_user_agent(self):
        """Get next user agent, rotating if needed"""
        self.request_count += 1
        
        if self.request_count % self.rotate_agent_after == 0:
            self.current_agent_index = (self.current_agent_index + 1) % len(self.user_agents)
            logging.info(f"Rotating user agent to: {self.user_agents[self.current_agent_index]}")
        
        return self.user_agents[self.current_agent_index]
    
    def get_stats(self):
        """Get rate limiting statistics"""
        elapsed_time = time.time() - self.start_time
        return {
            'requests_per_second': self.request_count / max(elapsed_time, 0.001),
            'elapsed_time': elapsed_time,
            'request_count': self.request_count
        }

def format_size(size_bytes):
    """Format size in bytes to human-readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

def is_valid_url(url):
    """Check if the URL is valid and well-formed"""
    try:
        parsed = urlparse(url)
        return bool(parsed.scheme) and bool(parsed.netloc) and parsed.scheme in ['http', 'https']
    except:
        return False

def analyze_url_structure(url):
    """Analyze URL structure and return metrics"""
    parsed_url = urlparse(url)
    path = parsed_url.path
    
    # URL length
    url_length = len(url)
    
    # URL parameters count
    params_count = len(parsed_url.query.split('&')) if parsed_url.query else 0
    
    # URL path depth
    path_parts = [p for p in path.split('/') if p]
    path_depth = len(path_parts)
    
    return {
        'url_length': url_length,
        'params_count': params_count,
        'path_depth': path_depth,
        'path_parts': path_parts
    }

def analyze_link_quality(soup, base_url):
    """Analyze link quality metrics"""
    domain = urlparse(base_url).netloc
    all_links = soup.find_all('a', href=True)
    
    # Initialize counters
    internal_links = []
    external_links = []
    nofollow_links = 0
    empty_anchor_texts = 0
    generic_anchor_texts = 0
    keyword_rich_anchor_texts = 0
    
    # Generic anchor text patterns
    generic_patterns = ['click here', 'read more', 'learn more', 'more info', 'details', 
                       'link', 'here', 'this', 'page', 'website', 'site']
    
    for link in all_links:
        href = link['href']
        full_url = urljoin(base_url, href)
        
        # Skip non-valid URLs
        if not is_valid_url(full_url):
            continue
            
        # Check if internal or external
        if urlparse(full_url).netloc == domain:
            internal_links.append(full_url)
        else:
            external_links.append(full_url)
        
        # Check for nofollow
        if link.get('rel') and 'nofollow' in link.get('rel'):
            nofollow_links += 1
        
        # Analyze anchor text
        anchor_text = link.get_text(strip=True).lower()
        if not anchor_text:
            empty_anchor_texts += 1
        elif any(pattern in anchor_text for pattern in generic_patterns):
            generic_anchor_texts += 1
        elif len(anchor_text.split()) >= 3:  # Assuming keyword-rich has 3+ words
            keyword_rich_anchor_texts += 1
    
    # Calculate ratios
    total_links = len(internal_links) + len(external_links)
    internal_external_ratio = len(internal_links) / max(len(external_links), 1)  # Avoid division by zero
    
    return {
        'internal_links': internal_links,
        'external_links': external_links,
        'internal_link_count': len(internal_links),
        'external_link_count': len(external_links),
        'nofollow_link_count': nofollow_links,
        'empty_anchor_text_count': empty_anchor_texts,
        'generic_anchor_text_count': generic_anchor_texts,
        'keyword_rich_anchor_text_count': keyword_rich_anchor_texts,
        'internal_external_ratio': internal_external_ratio,
        'total_link_count': total_links
    }

def count_resources(soup, url):
    """Count different types of resources on the page"""
    domain = urlparse(url).netloc
    
    # Initialize counters
    resources = {
        'js_files': 0,
        'css_files': 0,
        'images': 0,
        'fonts': 0,
        'videos': 0,
        'audios': 0,
        'other': 0,
        'internal_resources': 0,
        'external_resources': 0
    }
    
    # Count JavaScript files
    for script in soup.find_all('script', src=True):
        resources['js_files'] += 1
        src_url = urljoin(url, script['src'])
        if urlparse(src_url).netloc == domain:
            resources['internal_resources'] += 1
        else:
            resources['external_resources'] += 1
    
    # Count CSS files
    for css in soup.find_all('link', rel='stylesheet'):
        resources['css_files'] += 1
        href_url = urljoin(url, css['href']) if css.get('href') else ''
        if href_url and urlparse(href_url).netloc == domain:
            resources['internal_resources'] += 1
        elif href_url:
            resources['external_resources'] += 1
    
    # Count images
    for img in soup.find_all('img', src=True):
        resources['images'] += 1
        src_url = urljoin(url, img['src'])
        if urlparse(src_url).netloc == domain:
            resources['internal_resources'] += 1
        else:
            resources['external_resources'] += 1
    
    # Count fonts (approximation based on font-face in style tags and font URLs)
    for font_link in soup.find_all('link', href=re.compile(r'\\.(woff|woff2|ttf|eot)')):
        resources['fonts'] += 1
        href_url = urljoin(url, font_link['href'])
        if urlparse(href_url).netloc == domain:
            resources['internal_resources'] += 1
        else:
            resources['external_resources'] += 1
    
    # Count videos
    for video in soup.find_all(['video', 'iframe']):
        if video.name == 'video' or (video.name == 'iframe' and any(s in video.get('src', '') for s in ['youtube', 'vimeo', 'dailymotion'])):
            resources['videos'] += 1
            src_url = urljoin(url, video.get('src', ''))
            if src_url and urlparse(src_url).netloc == domain:
                resources['internal_resources'] += 1
            elif src_url:
                resources['external_resources'] += 1
    
    # Count audios
    for audio in soup.find_all('audio', src=True):
        resources['audios'] += 1
        src_url = urljoin(url, audio['src'])
        if urlparse(src_url).netloc == domain:
            resources['internal_resources'] += 1
        else:
            resources['external_resources'] += 1
    
    return resources

def extract_metadata(soup, url):
    """Extract metadata from the page"""
    metadata = {
        'title': soup.title.string if soup.title else "No Title",
        'meta_description': "",
        'meta_keywords': "",
        'favicon': "",
        'canonical_url': "",
        'og_title': "",
        'og_description': "",
        'og_image': "",
    }
    
    for meta in soup.find_all('meta'):
        if meta.get('name') == 'description':
            metadata['meta_description'] = meta.get('content', '')
        elif meta.get('name') == 'keywords':
            metadata['meta_keywords'] = meta.get('content', '')
        elif meta.get('property') == 'og:title':
            metadata['og_title'] = meta.get('content', '')
        elif meta.get('property') == 'og:description':
            metadata['og_description'] = meta.get('content', '')
        elif meta.get('property') == 'og:image':
            metadata['og_image'] = meta.get('content', '')

    favicon_link = soup.find('link', rel=re.compile(r'^(shortcut )?icon$', re.I))
    if favicon_link:
        metadata['favicon'] = urljoin(url, favicon_link.get('href', ''))
    
    canonical_link = soup.find('link', rel='canonical')
    if canonical_link:
        metadata['canonical_url'] = canonical_link.get('href', '')

    return metadata

def save_results(results):
    """Save results to JSON and CSV files"""
    os.makedirs('data', exist_ok=True)

    json_path = 'data/results.json'
    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(results, json_file, indent=4, ensure_ascii=False)

    csv_path = 'data/results.csv'
    if results:
        fieldnames = results[0].keys()
        with open(csv_path, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    # Save a simplified version for easier processing
    simple_json_path = 'data/simple_results.json'
    simple_results = []
    for result in results:
        simple_result = {
            'url': result['url'],
            'title': result['title'],
            'status_code': result['status_code'],
            'depth': result['depth'],
            'internal_link_count': result['internal_link_count'],
            'external_link_count': result['external_link_count'],
            'image_count': result['image_count'],
            'js_files_count': result.get('js_files_count', 0),
            'css_files_count': result.get('css_files_count', 0),
            'content_size': result['content_size'],
            'crawl_timestamp': result['crawl_timestamp']
        }
        simple_results.append(simple_result)
    
    with open(simple_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(simple_results, json_file, indent=4, ensure_ascii=False)

def crawl(url, depth, max_pages=100, timeout=10, requests_per_second=2, rotate_agent_after=10):
    """Main crawl function with smart rate limiting and user agent rotation"""
    visited = set()
    results = []
    page_count = 0
    rate_limiter = RateLimiter(
        initial_requests_per_second=requests_per_second,
        rotate_agent_after=rotate_agent_after
    )
    total_size = 0
    start_time = time.time()

    logging.info(f"""
Starting crawl with:
- URL: {url}
- Depth: {depth}
- Max Pages: {max_pages}
- Timeout: {timeout}s
- Rate Limit: {requests_per_second} req/s
- Agent Rotation: every {rotate_agent_after} requests
""")

    def _crawl(url, current_depth):
        nonlocal page_count, total_size

        if current_depth > depth or url in visited or page_count >= max_pages:
            return

        domain = urlparse(url).netloc
        visited.add(url)
        page_count += 1

        # Progress update
        elapsed_time = time.time() - start_time
        rate_stats = rate_limiter.get_stats()

        # Calculate totals so far
        total_images_so_far = sum(result.get('image_count', 0) for result in results)
        total_js_files = sum(result.get('js_files_count', 0) for result in results)
        total_css_files = sum(result.get('css_files_count', 0) for result in results)
        total_internal_links = sum(result.get('internal_link_count', 0) for result in results)
        total_external_links = sum(result.get('external_link_count', 0) for result in results)

        progress = f"""
Progress Update:
+- Pages: {page_count}/{max_pages} ({(page_count/max_pages*100):.1f}%)
   +- Depth: {current_depth}/{depth}
   +- Domain: {domain}
   +- Resources:
      +- Images: {total_images_so_far}
      +- JS Files: {total_js_files}
      +- CSS Files: {total_css_files}
   +- Links:
      +- Internal: {total_internal_links}
      +- External: {total_external_links}
   +- Data: {format_size(total_size)}
   +- Time: {elapsed_time:.1f}s
   +- Speed: {rate_stats['requests_per_second']:.2f} req/s
   +- Delay: {rate_limiter.delays[domain]:.2f}s
"""
        logging.info(progress)

        # Rate limiting and user agent rotation
        rate_limiter.wait(domain)
        headers = {'User-Agent': rate_limiter.get_next_user_agent()}

        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            content_size = len(response.content)
            total_size += content_size

            if response.status_code == 429:
                delay = rate_limiter.handle_429(domain)
                logging.warning(f"Rate limit hit for {domain}, waiting {delay}s...")
                time.sleep(delay)
                return

            response.raise_for_status()
            rate_limiter.handle_success(domain)

            if not response.headers.get('content-type', '').startswith('text/html'):
                logging.info(f"Skipping non-HTML content at {url}")
                return

            soup = BeautifulSoup(response.text, 'html.parser')
            metadata = extract_metadata(soup, url)

            # Analyze URL structure
            url_structure = analyze_url_structure(url)

            # Analyze links
            link_analysis = analyze_link_quality(soup, url)
            internal_links = link_analysis['internal_links']

            # Count resources
            resource_counts = count_resources(soup, url)

            # Count images (already counted in resource_counts but kept for backward compatibility)
            image_count = resource_counts['images']

            # Prepare result with all the new metrics
            result = {
                'url': url,
                'depth': current_depth,
                **metadata,
                # URL structure metrics
                'url_length': url_structure['url_length'],
                'url_params_count': url_structure['params_count'],
                'url_path_depth': url_structure['path_depth'],
                
                # Link metrics
                'internal_link_count': link_analysis['internal_link_count'],
                'external_link_count': link_analysis['external_link_count'],
                'nofollow_link_count': link_analysis['nofollow_link_count'],
                'empty_anchor_text_count': link_analysis['empty_anchor_text_count'],
                'generic_anchor_text_count': link_analysis['generic_anchor_text_count'],
                'keyword_rich_anchor_text_count': link_analysis['keyword_rich_anchor_text_count'],
                'internal_external_ratio': link_analysis['internal_external_ratio'],
                'total_link_count': link_analysis['total_link_count'],
                
                # Resource metrics
                'js_files_count': resource_counts['js_files'],
                'css_files_count': resource_counts['css_files'],
                'image_count': image_count,
                'font_count': resource_counts['fonts'],
                'video_count': resource_counts['videos'],
                'audio_count': resource_counts['audios'],
                'internal_resources_count': resource_counts['internal_resources'],
                'external_resources_count': resource_counts['external_resources'],
                
                # Basic metrics (kept for backward compatibility)
                'word_count': len(soup.get_text(separator=' ', strip=True).split()),
                'content_size': content_size,
                'crawl_timestamp': datetime.now().isoformat(),
                'status_code': response.status_code
            }

            results.append(result)

            for next_url in internal_links:
                if page_count < max_pages:
                    _crawl(next_url, current_depth + 1)

        except requests.Timeout:
            logging.error(f"Timeout error for {url}")
        except requests.RequestException as e:
            logging.error(f"Request failed for {url}: {e}")
        except Exception as e:
            logging.error(f"Unexpected error for {url}: {e}")

    _crawl(url, 0)

    # Calculate totals
    total_images = sum(result.get('image_count', 0) for result in results)
    total_js_files = sum(result.get('js_files_count', 0) for result in results)
    total_css_files = sum(result.get('css_files_count', 0) for result in results)
    total_fonts = sum(result.get('font_count', 0) for result in results)
    total_videos = sum(result.get('video_count', 0) for result in results)
    total_audios = sum(result.get('audio_count', 0) for result in results)
    
    total_internal_links = sum(result.get('internal_link_count', 0) for result in results)
    total_external_links = sum(result.get('external_link_count', 0) for result in results)
    total_nofollow_links = sum(result.get('nofollow_link_count', 0) for result in results)
    
    # Final summary
    stats = rate_limiter.get_stats()
    logging.info(f"""
Crawl Completed:
+- Pages: {page_count}
   +- Resources:
      +- Images: {total_images}
      +- JS Files: {total_js_files}
      +- CSS Files: {total_css_files}
      +- Fonts: {total_fonts}
      +- Videos: {total_videos}
      +- Audios: {total_audios}
   +- Links:
      +- Internal: {total_internal_links}
      +- External: {total_external_links}
      +- Nofollow: {total_nofollow_links}
   +- Data: {format_size(total_size)}
   +- Time: {stats['elapsed_time']:.1f}s
   +- Speed: {stats['requests_per_second']:.2f} req/s
""")

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='''
PagesXcrawler - Advanced Web Crawler with Smart Rate Limiting

Two ways to use this crawler:

1. Command Line Format:
   python crawler.py URL DEPTH [OPTIONS]

   Example:
   python crawler.py "https://example.com" 2 --max-pages 50 --timeout 15

2. GitHub Issues Format:
   crawl: URL DEPTH [OPTIONS]

   Example:
   crawl: https://example.com 2 --max-pages 50 --timeout 15
''',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  Basic usage:
    python crawler.py "https://example.com" 2

  With options:
    python crawler.py "https://example.com" 2 --max-pages 50 --timeout 15

  With user agent rotation:
    python crawler.py "https://example.com" 3 --rotate-agent-after 5

  Full example:
    python crawler.py "https://example.com" 3 --max-pages 50 --timeout 15 --requests-per-second 1 --rotate-agent-after 5

Note: Always enclose URLs in quotes to handle special characters correctly.
'''
    )

    parser.add_argument('url',
                       help='The URL to crawl (include http:// or https://)')

    parser.add_argument('depth', type=int,
                       help='How many levels deep to crawl (e.g., 2 for homepage and links from it)')

    parser.add_argument('--max-pages', type=int, default=100,
                       help='Maximum number of pages to crawl (default: 100)')

    parser.add_argument('--timeout', type=int, default=10,
                       help='Request timeout in seconds (default: 10)')

    parser.add_argument('--requests-per-second', type=float, default=2,
                       help='Initial rate limiting in requests per second (default: 2)')

    parser.add_argument('--rotate-agent-after', type=int, default=10,
                       help='Number of requests before rotating user agent (default: 10)')

    args = parser.parse_args()

    # URL validation
    if not is_valid_url(args.url):
        logging.error("Error: Invalid URL format. URL must start with http:// or https://")
        parser.print_help()
        exit(1)

    # Depth validation
    if args.depth < 0:
        logging.error("Error: Depth must be non-negative")
        parser.print_help()
        exit(1)

    # Rate limiting validation
    if args.requests_per_second <= 0:
        logging.error("Error: Requests per second must be positive")
        parser.print_help()
        exit(1)

    try:
        results = crawl(
            args.url,
            args.depth,
            args.max_pages,
            args.timeout,
            args.requests_per_second,
            args.rotate_agent_after
        )
        save_results(results)
        logging.info("Results saved successfully")
    except KeyboardInterrupt:
        logging.info("\nCrawl interrupted by user. Saving partial results...")
        if 'results' in locals() and results:
            save_results(results)
        exit(0)
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        if 'results' in locals() and results:
            save_results(results)
        exit(1)
