import json
import os
import csv
from collections import defaultdict
from urllib.parse import urlparse
import re
from datetime import datetime

def format_size(size):
    """Format size in bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} GB"

def format_number(num):
    """Format number with thousand separators"""
    return "{:,}".format(int(num))

def update_html():
    """Generate the HTML dashboard with crawl results"""
    json_path = 'data/results.json'
    csv_path = 'data/results.csv'
    
    results = []

    # Load data from JSON if available
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as json_file:
            results.extend(json.load(json_file))

    # Load data from CSV if available
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                for key in ['h1_tags', 'h2_tags', 'link_texts']:
                    if isinstance(row.get(key), str):
                        row[key] = eval(row[key]) if row[key] else []
                results.append(row)

    # Process data for visualization
    domains = defaultdict(int)
    content_types = defaultdict(int)
    total_words = 0
    total_images = 0
    depths = set()

    for result in results:
        domain = urlparse(result['url']).netloc
        domains[domain] += 1
        if 'content_type' in result:
            content_type = result['content_type'].split(';')[0].strip()
            content_types[content_type] += 1
        total_words += int(result.get('word_count', 0))
        total_images += int(result.get('image_count', 0))
        depths.add(int(result.get('depth', 0)))

    styles = """
        :root {
            --primary-color: #3b82f6;
            --primary-dark: #2563eb;
            --primary-light: #93c5fd;
            --secondary-color: #64748b;
            --background-color: #f1f5f9;
            --card-background: #ffffff;
            --text-color: #1e293b;
            --border-color: #e2e8f0;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--background-color);
            color: var(--text-color);
            line-height: 1.5;
            min-height: 100vh;
        }

        .container {
            width: 100%;
            max-width: 1600px;
            margin: 0 auto;
            padding: 2rem;
        }

        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
            margin-top: 2rem;
        }

        .results-container {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 2rem;
            margin: 2rem 0;
        }

        @media (min-width: 640px) {
            .results-container { 
                grid-template-columns: repeat(1, 1fr); 
            }
        }

        @media (min-width: 768px) {
            .results-container { 
                grid-template-columns: repeat(2, 1fr); 
            }
        }

        @media (min-width: 1024px) {
            .results-container { 
                grid-template-columns: repeat(3, 1fr); 
            }
        }

        @media (min-width: 1280px) {
            .results-container { 
                grid-template-columns: repeat(4, 1fr); 
            }
        }

        .result-card {
            background: var(--card-background);
            border-radius: 1rem;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            border: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            gap: 1rem;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .result-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
            border-color: var(--primary-light);
        }

        .filters {
            background: var(--card-background);
            padding: 1.5rem;
            border-radius: 1rem;
            margin: 2rem 0;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .filter-group {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }

        .filter-group label {
            font-size: 0.875rem;
            font-weight: 600;
            color: var(--secondary-color);
        }

        .filter-group select,
        .filter-group input {
            padding: 0.75rem;
            border: 1px solid var(--border-color);
            border-radius: 0.5rem;
            font-size: 0.875rem;
            width: 100%;
            transition: all 0.2s;
        }

        .filter-group select:focus,
        .filter-group input:focus {
            outline: none;
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px var(--primary-light);
        }

        .stat-card {
            background: var(--card-background);
            padding: 1.5rem;
            border-radius: 1rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }

        .stat-card h3 {
            color: var(--secondary-color);
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .stat-card .value {
            font-size: 2rem;
            font-weight: 600;
            color: var(--primary-color);
        }

        .title {
            font-size: 1.875rem;
            font-weight: 600;
            color: var(--primary-color);
            margin: 2rem 0;
            text-align: center;
        }

        .card-header {
            margin-bottom: 1rem;
        }

        .card-stats {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
            padding: 1rem;
            background: var(--background-color);
            border-radius: 0.5rem;
            margin-top: auto;
        }

        .stat-item {
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }

        .meta-info {
            font-size: 0.875rem;
            color: var(--secondary-color);
            margin-top: 0.5rem;
        }

        .value {
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--primary-color);
        }

        .url {
            color: var(--primary-dark);
            text-decoration: none;
            word-break: break-all;
        }

        .url:hover {
            text-decoration: underline;
        }

        .tag {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            background: var(--primary-light);
            color: var(--primary-dark);
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
    """

    # Write HTML content
    with open('index.html', 'w', encoding='utf-8') as html_file:
        html_file.write(f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crawler Results Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        {styles}
    </style>
</head>
<body>
    <div class="container">
        <h1 class="title">Crawler Results Dashboard</h1>
        
        <div class="dashboard">
            <div class="stat-card">
                <h3>Pages Crawled</h3>
                <div class="value">{format_number(len(results))}</div>
            </div>
            <div class="stat-card">
                <h3>Total Words</h3>
                <div class="value">{format_number(total_words)}</div>
            </div>
            <div class="stat-card">
                <h3>Total Images</h3>
                <div class="value">{format_number(total_images)}</div>
            </div>
            <div class="stat-card">
                <h3>Domains</h3>
                <div class="value">{format_number(len(domains))}</div>
            </div>
        </div>

        <div class="filters">
            <div class="filter-group">
                <label for="searchInput">Search Content</label>
                <input type="text" id="searchInput" placeholder="Enter keywords...">
            </div>
            <div class="filter-group">
                <label for="domainFilter">Filter by Domain</label>
                <select id="domainFilter">
                    <option value="">All Domains</option>''')

        # Add domain options
        for domain in sorted(domains):
            count = domains[domain]
            html_file.write(f'<option value="{domain}">{domain} ({count})</option>')

        html_file.write('''
                </select>
            </div>
            <div class="filter-group">
                <label for="depthFilter">Filter by Depth</label>
                <select id="depthFilter">
                    <option value="">All Depths</option>''')

        # Add depth options
        for depth in sorted(depths):
            html_file.write(f'<option value="{depth}">Depth {depth}</option>')

        html_file.write('''
                </select>
            </div>
        </div>

        <div class="results-container">''')

        # Add result cards
        for result in results:
            url = result.get('url', 'N/A')
            domain = urlparse(url).netloc
            depth = result.get('depth', 'N/A')
            title = result.get('title', 'No Title')
            word_count = int(result.get('word_count', 0))
            image_count = int(result.get('image_count', 0))
            internal_links = int(result.get('internal_link_count', 0))
            external_links = int(result.get('external_link_count', 0))

            html_file.write(f'''
            <div class="result-card" data-domain="{domain}" data-depth="{depth}">
                <div class="card-header">
                    <span class="tag">Depth {depth}</span>
                    <h2 class="title">{title}</h2>
                    <a href="{url}" target="_blank" class="url">{url}</a>
                </div>
                <div class="card-stats">
                    <div class="stat-item">
                        <span class="meta-info">Words</span>
                        <span class="value">{format_number(word_count)}</span>
                    </div>
                    <div class="stat-item">
                        <span class="meta-info">Images</span>
                        <span class="value">{format_number(image_count)}</span>
                    </div>
                    <div class="stat-item">
                        <span class="meta-info">Internal Links</span>
                        <span class="value">{format_number(internal_links)}</span>
                    </div>
                    <div class="stat-item">
                        <span class="meta-info">External Links</span>
                        <span class="value">{format_number(external_links)}</span>
                    </div>
                </div>''')

            if result.get('meta_description'):
                html_file.write(f'''
                <div class="meta-info">
                    <strong>Description:</strong> {result['meta_description']}
                </div>''')

            if result.get('meta_keywords'):
                html_file.write(f'''
                <div class="meta-info">
                    <strong>Keywords:</strong> {result['meta_keywords']}
                </div>''')

            html_file.write('\n            </div>')

        # Close containers and add JavaScript
        html_file.write('''
        </div>
    </div>
    <script>
        function filterResults() {
            const searchInput = document.getElementById('searchInput').value.toLowerCase();
            const domainFilter = document.getElementById('domainFilter').value;
            const depthFilter = document.getElementById('depthFilter').value;
            const cards = document.getElementsByClassName('result-card');

            Array.from(cards).forEach(card => {
                const content = card.textContent.toLowerCase();
                const domain = card.getAttribute('data-domain');
                const depth = card.getAttribute('data-depth');

                const matchesSearch = content.includes(searchInput);
                const matchesDomain = !domainFilter || domain === domainFilter;
                const matchesDepth = !depthFilter || depth === depthFilter;

                if (matchesSearch && matchesDomain && matchesDepth) {
                    card.style.display = 'flex';
                } else {
                    card.style.display = 'none';
                }
            });
        }

        document.getElementById('searchInput').addEventListener('input', filterResults);
        document.getElementById('domainFilter').addEventListener('change', filterResults);
        document.getElementById('depthFilter').addEventListener('change', filterResults);
    </script>
</body>
</html>
''')

if __name__ == "__main__":
    update_html()
