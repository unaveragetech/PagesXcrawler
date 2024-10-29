import requests
from bs4 import BeautifulSoup
import json
import csv
import os
from urllib.parse import urljoin, urlparse

def crawl(url, depth):
    visited = set()
    results = []

    def _crawl(url, current_depth):
        if current_depth > depth or url in visited:
            return
        visited.add(url)
        try:
            response = requests.get(url, timeout=5)  # Set a timeout for requests
            response.raise_for_status()  # Raise an error for bad responses
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Gather additional information
            title = soup.title.string if soup.title else "No Title"
            meta_description = ""
            meta_tag = soup.find("meta", attrs={"name": "description"})
            if meta_tag:
                meta_description = meta_tag.get("content", "No Description")

            # Count internal and external links
            internal_links = []
            external_links = []
            for link in soup.find_all('a', href=True):
                full_url = urljoin(url, link['href'])
                if is_valid_url(full_url):
                    if urlparse(full_url).netloc == urlparse(url).netloc:
                        internal_links.append(full_url)
                    else:
                        external_links.append(full_url)
            
            # Word count on the page
            words = soup.get_text().split()
            word_count = len(words)

            results.append({
                'url': url,
                'depth': current_depth,
                'title': title,
                'meta_description': meta_description,
                'internal_link_count': len(internal_links),
                'external_link_count': len(external_links),
                'word_count': word_count
            })
            
            for next_url in internal_links:
                _crawl(next_url, current_depth + 1)
                
        except requests.RequestException as e:
            print(f"Request failed for {url}: {e}")  # Log the error

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
    with open(csv_path, 'w', newline='') as csv_file:
        fieldnames = [
            'url', 'depth', 'title', 'meta_description', 
            'internal_link_count', 'external_link_count', 'word_count'
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
