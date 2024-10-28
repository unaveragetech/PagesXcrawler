# This script defines a simple web crawler that takes a URL and a depth argument.
# It crawls the specified URL, retrieves all links up to the specified depth,
# and saves the results in both JSON and CSV formats.

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
            results.append({'url': url, 'depth': current_depth})
            for link in soup.find_all('a', href=True):
                next_url = urljoin(url, link['href'])
                if is_valid_url(next_url) and urlparse(next_url).netloc == urlparse(url).netloc:  # Stay on the same domain
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
        fieldnames = ['url', 'depth']
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
