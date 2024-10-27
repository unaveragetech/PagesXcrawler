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
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            results.append({'url': url, 'depth': current_depth})
            for link in soup.find_all('a', href=True):
                next_url = urljoin(url, link['href'])
                if urlparse(next_url).netloc == urlparse(url).netloc:  # Stay on the same domain
                    _crawl(next_url, current_depth + 1)
        except requests.RequestException:
            pass  # Handle any connection errors silently

    _crawl(url, 0)
    return results

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

def parse_url_with_depth(url_with_depth):
    # Separate the URL and depth from the format 'https://example.com:depth'
    if ':' in url_with_depth:
        url, depth_str = url_with_depth.rsplit(':', 1)
        try:
            depth = int(depth_str)
        except ValueError:
            print("Invalid depth provided. Defaulting to depth 1.")
            depth = 1
        return url, depth
    return url_with_depth, 1  # Default depth to 1 if not specified

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python crawler.py <url:depth>")
    else:
        url_with_depth = sys.argv[1]
        url, depth = parse_url_with_depth(url_with_depth)
        results = crawl(url, depth)
        save_results(results)
