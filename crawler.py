import requests
from bs4 import BeautifulSoup
import json
import csv
import os
import random
from urllib.parse import urljoin, urlparse

# Extended list of user agents for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
    'Mozilla/5.0 (Linux; Android 9; SM-A750F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36'
]

def crawl(url, depth):
    visited = set()
    results = []

    def _crawl(url, current_depth):
        if current_depth > depth or url in visited:
            return
        visited.add(url)
        
        # Rotate user agent for each request
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        
        try:
            response = requests.get(url, headers=headers, timeout=5)  # Set a timeout for requests
            response.raise_for_status()  # Raise an error for bad responses
            content_type = response.headers.get('Content-Type', '')

            # Skip non-HTML content
            if 'text/html' not in content_type:
                print(f"Skipping non-HTML content at {url}")
                return

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Gather additional information
            title = soup.title.string if soup.title else "No Title"
            meta_description = ""
            meta_keywords = ""
            meta_tag = soup.find("meta", attrs={"name": "description"})
            keywords_tag = soup.find("meta", attrs={"name": "keywords"})
            if meta_tag:
                meta_description = meta_tag.get("content", "No Description")
            if keywords_tag:
                meta_keywords = keywords_tag.get("content", "No Keywords")

            # Count internal and external links
            internal_links = []
            external_links = []
            link_texts = []
            for link in soup.find_all('a', href=True):
                full_url = urljoin(url, link['href'])
                if is_valid_url(full_url):
                    link_texts.append(link.get_text(strip=True))
                    if urlparse(full_url).netloc == urlparse(url).netloc:
                        internal_links.append(full_url)
                    else:
                        external_links.append(full_url)
            
            # Word count on the page
            words = soup.get_text(separator=' ', strip=True).split()
            word_count = len(words)

            # Additional content scraping (e.g., H1 tags, H2 tags, main content)
            h1_tags = [h1.get_text(strip=True) for h1 in soup.find_all('h1')]
            h2_tags = [h2.get_text(strip=True) for h2 in soup.find_all('h2')]
            main_content = soup.find('main')
            main_text = main_content.get_text(strip=True) if main_content else ""
            main_word_count = len(main_text.split()) if main_text else 0

            # Count images
            image_count = len(soup.find_all('img'))

            results.append({
                'url': url,
                'depth': current_depth,
                'title': title,
                'meta_description': meta_description,
                'meta_keywords': meta_keywords,
                'internal_link_count': len(internal_links),
                'external_link_count': len(external_links),
                'word_count': word_count,
                'h1_tags': h1_tags,
                'h2_tags': h2_tags,
                'main_word_count': main_word_count,
                'image_count': image_count,
                'link_texts': link_texts,
                'content_type': content_type
            })
            
            for next_url in internal_links:
                _crawl(next_url, current_depth + 1)
                
        except requests.RequestException as e:
            print(f"Request failed for {url}: {e}")  # Log the error
        except Exception as e:
            print(f"An error occurred for {url}: {e}")  # Log unexpected errors

    _crawl(url, 0)
    return results

def is_valid_url(url):
    """Check if the URL is valid and well-formed."""
    parsed = urlparse(url)
    return bool(parsed.scheme) and bool(parsed.netloc)

def save_results(results):
    # Save results to JSON
    json_path = 'data/results.json'
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, 'w') as json_file:
        json.dump(results, json_file, indent=4)

    # Save results to CSV
    csv_path = 'data/results.csv'
    with open(csv_path, 'w', newline='', encoding='utf-8') as csv_file:
        fieldnames = [
            'url', 'depth', 'title', 'meta_description', 
            'meta_keywords', 'internal_link_count', 'external_link_count', 
            'word_count', 'h1_tags', 'h2_tags', 'main_word_count', 
            'image_count', 'link_texts', 'content_type'
        ]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python crawler.py <url> <depth>")
        sys.exit(1)

    url = sys.argv[1]
    depth = sys.argv[2]

    if not depth.isdigit() or int(depth) < 0:
        print("Depth must be a non-negative integer.")
        sys.exit(1)

    depth = int(depth)

    if not is_valid_url(url):
        print("Error: Invalid URL format.")
        sys.exit(1)

    results = crawl(url, depth)
    save_results(results)
