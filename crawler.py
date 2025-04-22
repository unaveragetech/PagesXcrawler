import requests
from bs4 import BeautifulSoup
import json
import csv
import os
import random
import time
import logging
import argparse
from collections import defaultdict
from urllib.parse import urljoin, urlparse
import re
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

# User Agent Categories for better organization and reference
USER_AGENTS = {
    "windows_chrome": [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
    ],
    "windows_firefox": [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0'
    ],
    "windows_edge": [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 Edg/92.0.902.84'
    ],
    "macos_safari": [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_5_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15'
    ],
    "macos_chrome": [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_5_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
    ],
    "macos_firefox": [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:90.0) Gecko/20100101 Firefox/90.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 11.5; rv:91.0) Gecko/20100101 Firefox/91.0'
    ],
    "linux_chrome": [
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
    ],
    "linux_firefox": [
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0'
    ],
    "mobile_android": [
        'Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 11; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Mobile Safari/537.36'
    ],
    "mobile_ios": [
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1'
    ]
}

# Flatten USER_AGENTS for use in rotation
ALL_USER_AGENTS = [agent for agents in USER_AGENTS.values() for agent in agents]

class RateLimiter:
    def __init__(self, initial_requests_per_second=2, rotate_agent_after=10):
        self.delays = defaultdict(lambda: 1.0 / initial_requests_per_second)
        self.last_request = defaultdict(float)
        self.consecutive_429s = defaultdict(int)
        self.backoff_factor = 2
        self.max_delay = 60
        self.total_requests = 0
        self.start_time = time.time()
        self.user_agents = ALL_USER_AGENTS.copy()
        random.shuffle(self.user_agents)
        self.user_agent_index = 0
        self.rotate_after = rotate_agent_after
        self.requests_since_rotation = 0

    def wait(self, domain):
        current_time = time.time()
        time_passed = current_time - self.last_request[domain]
        if time_passed < self.delays[domain]:
            time.sleep(self.delays[domain] - time_passed)
        self.last_request[domain] = time.time()
        self.total_requests += 1
    
    def get_next_user_agent(self):
        """Get the next user agent, rotating if necessary"""
        self.requests_since_rotation += 1
        
        # Rotate if we've hit the threshold
        if self.requests_since_rotation >= self.rotate_after:
            self.user_agent_index = (self.user_agent_index + 1) % len(self.user_agents)
            self.requests_since_rotation = 0
            logging.info(f"Rotating user agent to: {self.user_agents[self.user_agent_index]}")
        
        return self.user_agents[self.user_agent_index]
    
    def handle_429(self, domain):
        """Handle 429 Too Many Requests error with exponential backoff"""
        self.consecutive_429s[domain] += 1
        self.delays[domain] = min(
            self.delays[domain] * (self.backoff_factor ** self.consecutive_429s[domain]),
            self.max_delay
        )
        logging.warning(f"Rate limit detected for {domain}. Increasing delay to {self.delays[domain]:.2f} seconds")
        return self.delays[domain]
    
    def handle_success(self, domain):
        """Handle successful request by gradually reducing delay"""
        if self.consecutive_429s[domain] > 0:
            self.consecutive_429s[domain] = 0
            self.delays[domain] = max(self.delays[domain] / self.backoff_factor, 0.5)

    def get_stats(self):
        elapsed_time = time.time() - self.start_time
        return {
            'total_requests': self.total_requests,
            'elapsed_time': elapsed_time,
            'requests_per_second': self.total_requests / elapsed_time if elapsed_time > 0 else 0
        }

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
    """Check if the URL is valid and well-formed."""
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

def crawl(url, depth, max_pages=100, timeout=10, rotate_agent_after=10):
    """Main crawl function with user agent rotation"""
    visited = set()
    results = []
    page_count = 0
    rate_limiter = RateLimiter(rotate_agent_after=rotate_agent_after)
    total_size = 0
    start_time = time.time()

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
        
        progress = f"""
Progress Update:
+- Pages: {page_count}/{max_pages} ({(page_count/max_pages*100):.1f}%)
   +- Depth: {current_depth}/{depth}
   +- Domain: {domain}
   +- Data: {total_size} bytes
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
            total_size += len(response.content)
            
            if response.status_code == 429:
                delay = rate_limiter.handle_429(domain)
                time.sleep(delay)
                return
            
            response.raise_for_status()
            rate_limiter.handle_success(domain)
            
            if not response.headers.get('content-type', '').startswith('text/html'):
                logging.info(f"Skipping non-HTML content at {url}")
                return

            soup = BeautifulSoup(response.text, 'html.parser')
            metadata = extract_metadata(soup, url)
            
            # Process links and content
            internal_links = []
            external_links = []
            for link in soup.find_all('a', href=True):
                full_url = urljoin(url, link['href'])
                if is_valid_url(full_url):
                    if urlparse(full_url).netloc == domain:
                        internal_links.append(full_url)
                    else:
                        external_links.append(full_url)
            
            result = {
                'url': url,
                'depth': current_depth,
                **metadata,
                'internal_link_count': len(internal_links),
                'external_link_count': len(external_links),
                'word_count': len(soup.get_text(separator=' ', strip=True).split()),
                'content_size': len(response.content),
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
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Web crawler with enhanced capabilities')
    parser.add_argument('url', help='URL to crawl')
    parser.add_argument('depth', type=int, help='Maximum crawl depth')
    parser.add_argument('--max-pages', type=int, default=100, help='Maximum number of pages to crawl')
    parser.add_argument('--timeout', type=int, default=10, help='Request timeout in seconds')
    parser.add_argument('--rotate-agent-after', type=int, default=10, 
                      help='Number of requests after which to rotate user agent')

    args = parser.parse_args()

    if not is_valid_url(args.url):
        logging.error("Error: Invalid URL format.")
        exit(1)

    if args.depth < 0:
        logging.error("Error: Depth must be non-negative.")
        exit(1)

    try:
        results = crawl(args.url, args.depth, args.max_pages, args.timeout, args.rotate_agent_after)
        save_results(results)
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
