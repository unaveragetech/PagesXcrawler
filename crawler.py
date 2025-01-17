import requests
from bs4 import BeautifulSoup
import json
import csv
import os
import random
from urllib.parse import urljoin, urlparse
import PyPDF2
from io import BytesIO

# Extended list of user agents for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    # ... (other user agents)
]

def crawl(url, depth):
    visited = set()
    results = []

    def _crawl(url, current_depth):
        if current_depth > depth or url in visited:
            return
        visited.add(url)
        
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        
        try:
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            
            content_type = response.headers.get('Content-Type', 'unknown')
            result = {
                'url': url,
                'depth': current_depth,
                'content_type': content_type,
            }
            
            if 'text/html' in content_type:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                title = soup.title.string if soup.title else "No Title"
                meta_description = ""
                meta_keywords = ""
                meta_tag = soup.find("meta", attrs={"name": "description"})
                keywords_tag = soup.find("meta", attrs={"name": "keywords"})
                if meta_tag:
                    meta_description = meta_tag.get("content", "No Description")
                if keywords_tag:
                    meta_keywords = keywords_tag.get("content", "No Keywords")
                
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
                
                words = soup.get_text(separator=' ', strip=True).split()
                word_count = len(words)
                
                h1_tags = [h1.get_text(strip=True) for h1 in soup.find_all('h1')]
                h2_tags = [h2.get_text(strip=True) for h2 in soup.find_all('h2')]
                main_content = soup.find('main')
                main_text = main_content.get_text(strip=True) if main_content else ""
                main_word_count = len(main_text.split()) if main_text else 0
                
                image_count = len(soup.find_all('img'))
                
                result.update({
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
                    'link_texts': link_texts
                })
                
                for next_url in internal_links:
                    _crawl(next_url, current_depth + 1)
                    
            elif 'application/pdf' in content_type:
                pdf_reader = PyPDF2.PdfFileReader(BytesIO(response.content))
                extracted_text = ""
                for page in range(pdf_reader.getNumPages()):
                    extracted_text += pdf_reader.getPage(page).extractText()
                result.update({
                    'extracted_text': extracted_text,
                    'page_count': pdf_reader.getNumPages()
                })
                
            else:
                # For other content types, record basic information
                content_size = len(response.content)
                result.update({
                    'content_size': content_size
                })
                
            results.append(result)
            
        except requests.RequestException as e:
            print(f"Request failed for {url}: {e}")
        except PyPDF2.utils.PdfReadError as e:
            print(f"Error reading PDF for {url}: {e}")
        except Exception as e:
            print(f"An error occurred for {url}: {e}")

    _crawl(url, 0)
    return results

def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.scheme) and bool(parsed.netloc)

def save_results(results):
    json_path = 'data/results.json'
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, 'w') as json_file:
        json.dump(results, json_file, indent=4, default=str)
    
    csv_path = 'data/results.csv'
    with open(csv_path, 'w', newline='', encoding='utf-8') as csv_file:
        fieldnames = [
            'url', 'depth', 'content_type', 'title', 'meta_description', 
            'meta_keywords', 'internal_link_count', 'external_link_count', 
            'word_count', 'h1_tags', 'h2_tags', 'main_word_count', 
            'image_count', 'link_texts', 'extracted_text', 'page_count', 
            'content_size'
        ]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            # Convert lists to comma-separated strings for CSV
            row['h1_tags'] = ', '.join(row.get('h1_tags', []))
            row['h2_tags'] = ', '.join(row.get('h2_tags', []))
            row['link_texts'] = ', '.join(row.get('link_texts', []))
            writer.writerow(row)

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
