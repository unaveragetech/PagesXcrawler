import requests
from bs4 import BeautifulSoup
import json
import csv
import os
import random
import time
import logging
import argparse
import re
from collections import defaultdict, Counter
from urllib.parse import urljoin, urlparse, parse_qs
from datetime import datetime
import cssutils
import tinycss
import cssselect
from html import unescape
import validators
import colorama

# Suppress cssutils logging
cssutils.log.setLevel(logging.FATAL)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crawler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

[Previous USER_AGENTS and RateLimiter code remains the same...]

def analyze_heading_structure(soup):
    """Analyze heading hierarchy and structure"""
    headings = {f'h{i}': len(soup.find_all(f'h{i}')) for i in range(1, 7)}
    heading_order = []
    for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        heading_order.append(int(tag.name[1]))
    
    return {
        'heading_counts': headings,
        'heading_order': heading_order,
        'has_valid_hierarchy': all(x >= y for x, y in zip(heading_order, heading_order[1:]))
    }

def analyze_content_types(soup, response):
    """Analyze content types and ratios"""
    text_content = soup.get_text(strip=True)
    html_content = str(soup)
    scripts = soup.find_all('script')
    styles = soup.find_all('style')
    
    return {
        'text_length': len(text_content),
        'html_length': len(html_content),
        'text_html_ratio': len(text_content) / len(html_content) if html_content else 0,
        'script_count': len(scripts),
        'style_count': len(styles),
        'script_size': sum(len(str(s)) for s in scripts),
        'style_size': sum(len(str(s)) for s in styles)
    }

def analyze_page_structure(soup):
    """Analyze DOM structure and elements"""
    return {
        'dom_elements': len(soup.find_all()),
        'dom_depth': max(len(list(el.parents)) for el in soup.find_all()),
        'div_count': len(soup.find_all('div')),
        'span_count': len(soup.find_all('span')),
        'p_count': len(soup.find_all('p')),
        'list_count': len(soup.find_all(['ul', 'ol'])),
        'table_count': len(soup.find_all('table'))
    }

def analyze_forms(soup):
    """Analyze forms and input fields"""
    forms = soup.find_all('form')
    form_data = []
    
    for form in forms:
        inputs = form.find_all('input')
        required = len([i for i in inputs if i.get('required')])
        form_data.append({
            'method': form.get('method', 'get').lower(),
            'action': form.get('action', ''),
            'input_count': len(inputs),
            'required_fields': required,
            'input_types': Counter(i.get('type', 'text') for i in inputs)
        })
    
    return {
        'form_count': len(forms),
        'total_inputs': sum(f['input_count'] for f in form_data),
        'total_required': sum(f['required_fields'] for f in form_data),
        'forms': form_data
    }

def analyze_meta_tags(soup):
    """Analyze meta tags and SEO elements"""
    meta_tags = soup.find_all('meta')
    meta_data = {
        'title': soup.title.string if soup.title else None,
        'title_length': len(soup.title.string) if soup.title else 0,
        'description': None,
        'keywords': None,
        'robots': None,
        'viewport': None,
        'charset': None,
        'canonical': None,
        'og_tags': [],
        'twitter_cards': []
    }
    
    for tag in meta_tags:
        name = tag.get('name', '').lower()
        property = tag.get('property', '').lower()
        content = tag.get('content', '')
        
        if name == 'description':
            meta_data['description'] = content
        elif name == 'keywords':
            meta_data['keywords'] = content
        elif name == 'robots':
            meta_data['robots'] = content
        elif name == 'viewport':
            meta_data['viewport'] = content
        elif property.startswith('og:'):
            meta_data['og_tags'].append({'property': property, 'content': content})
        elif property.startswith('twitter:'):
            meta_data['twitter_cards'].append({'property': property, 'content': content})
    
    canonical = soup.find('link', rel='canonical')
    if canonical:
        meta_data['canonical'] = canonical.get('href')
    
    return meta_data

def analyze_schema_markup(soup):
    """Analyze schema.org structured data"""
    schemas = []
    for tag in soup.find_all():
        if tag.get('itemtype'):
            schemas.append({
                'type': tag.get('itemtype'),
                'props': len(tag.find_all(attrs={'itemprop': True}))
            })
    return schemas

def analyze_content_keywords(soup):
    """Analyze keyword density and distribution"""
    # Get text content and clean it
    text = soup.get_text(' ', strip=True).lower()
    words = re.findall(r'\b\w+\b', text)
    
    # Remove common stop words (expanded list)
    stop_words = {'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at'}
    words = [w for w in words if w not in stop_words and len(w) > 2]
    
    # Calculate word frequency
    word_freq = Counter(words)
    total_words = len(words)
    
    return {
        'total_words': total_words,
        'unique_words': len(word_freq),
        'top_keywords': dict(word_freq.most_common(20)),
        'keyword_density': {word: count/total_words for word, count in word_freq.most_common(20)} if total_words else {}
    }

def analyze_url_structure(url):
    """Analyze URL structure and parameters"""
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    
    return {
        'scheme': parsed.scheme,
        'netloc': parsed.netloc,
        'path': parsed.path,
        'path_length': len(parsed.path),
        'path_segments': len([s for s in parsed.path.split('/') if s]),
        'query_params': len(params),
        'param_names': list(params.keys()),
        'has_fragment': bool(parsed.fragment)
    }

def analyze_links(soup, base_url):
    """Analyze links and their attributes"""
    links = soup.find_all('a')
    link_data = {
        'total': len(links),
        'internal': 0,
        'external': 0,
        'nofollow': 0,
        'empty_anchors': 0,
        'generic_anchors': 0,
        'broken_links': 0,
        'anchor_text': []
    }
    
    generic_anchors = {'click here', 'read more', 'learn more', 'click', 'here', 'link'}
    
    for link in links:
        href = link.get('href')
        if not href:
            link_data['empty_anchors'] += 1
            continue
            
        # Clean and normalize anchor text
        anchor_text = link.get_text(strip=True).lower()
        link_data['anchor_text'].append(anchor_text)
        
        if anchor_text in generic_anchors:
            link_data['generic_anchors'] += 1
        
        # Check if internal or external
        if href.startswith(('http://', 'https://')):
            if urlparse(href).netloc == urlparse(base_url).netloc:
                link_data['internal'] += 1
            else:
                link_data['external'] += 1
        else:
            link_data['internal'] += 1
        
        # Check for nofollow
        if 'nofollow' in link.get('rel', []):
            link_data['nofollow'] += 1
    
    return link_data

def analyze_media(soup, base_url):
    """Analyze images, videos, and other media"""
    images = soup.find_all('img')
    media_data = {
        'images': {
            'total': len(images),
            'missing_alt': 0,
            'empty_alt': 0,
            'responsive': 0,
            'formats': defaultdict(int),
            'sizes': []
        },
        'videos': {
            'total': 0,
            'youtube': 0,
            'vimeo': 0,
            'other': 0
        },
        'audio': len(soup.find_all('audio')),
        'total_media_size': 0
    }
    
    # Analyze images
    for img in images:
        if not img.get('alt'):
            media_data['images']['missing_alt'] += 1
        elif img.get('alt').strip() == '':
            media_data['images']['empty_alt'] += 1
        
        if img.get('srcset') or img.get('sizes'):
            media_data['images']['responsive'] += 1
        
        src = img.get('src', '')
        if src:
            ext = os.path.splitext(src)[1].lower()
            media_data['images']['formats'][ext] += 1
    
    # Analyze videos
    iframes = soup.find_all('iframe')
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

def is_valid_url(url):
    """Check if the URL is valid and well-formed"""
    try:
        parsed = urlparse(url)
        return bool(parsed.scheme) and bool(parsed.netloc) and parsed.scheme in ['http', 'https']
    except:
        return False

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
            external_links = link_analysis['external_links']

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
   url:depth(n):params(key1=value1,key2=value2)

   Example:
   https://example.com:depth(2):params(max-pages=50,timeout=15)
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
        if results:
            save_results(results)
        exit(0)
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        if results:
            save_results(results)
        exit(1)

Two ways to use this crawler:

1. Command Line Format:
   python crawler.py URL DEPTH [OPTIONS]

   Example:
   python crawler.py "https://example.com" 2 --max-pages 50 --timeout 15

2. GitHub Issues Format:
   url:depth(n):params(key1=value1,key2=value2)

   Example:
   https://example.com:depth(2):params(max-pages=50,timeout=15)
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
        if results:
            save_results(results)
        exit(0)
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        if results:
            save_results(results)
        exit(1)
