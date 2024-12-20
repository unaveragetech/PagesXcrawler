# This script updates the `index.html` file with the latest results from `results.json` and `results.csv`.
# It processes the data, adds formatting, and generates a more readable webpage for the GitHub Pages site.

import json
import os
import csv

def update_html():
    json_path = 'data/results.json'
    csv_path = 'data/results.csv'
    
    results = []

    # Load data from JSON if available
    if os.path.exists(json_path):
        with open(json_path, 'r') as json_file:
            results.extend(json.load(json_file))

    # Load data from CSV if available
    if os.path.exists(csv_path):
        with open(csv_path, 'r') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                results.append(row)
    
    # Start building the HTML structure
    with open('index.html', 'w') as html_file:
        html_file.write('<!DOCTYPE html>\n<html lang="en">\n<head>\n')
        html_file.write('<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n')
        html_file.write('<title>🅿🅰🅶🅴🆂🆇🅲🆁🅰🆆🅻🅴🆁 ٩ʕ◕౪◕ʔو.url  ٩ʕ◕౪◕ʔو hmm. --Web Crawler System--</title>\n')
        html_file.write('<style>\n')
        html_file.write('body { font-family: Arial, sans-serif; margin: 0; display: flex; }\n')
        html_file.write('.sidebar { width: 250px; background-color: #f4f4f4; padding: 20px; overflow-y: auto; height: 100vh; }\n')
        html_file.write('.content { flex: 1; padding: 20px; }\n')
        html_file.write('h1 { color: #333; }\n')
        html_file.write('.results-container { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 15px; }\n')
        html_file.write('.result-card { border: 1px solid #ddd; border-radius: 8px; padding: 15px; background-color: #ffffff; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1); }\n')
        html_file.write('.result-card h3 { font-size: 18px; color: #007BFF; }\n')
        html_file.write('.result-card p { margin: 5px 0; font-size: 14px; }\n')
        html_file.write('.url { font-weight: bold; color: #007BFF; }\n')
        html_file.write('.sidebar ul { list-style-type: none; padding: 0; }\n')
        html_file.write('.sidebar ul li { margin: 10px 0; }\n')
        html_file.write('.sidebar a { text-decoration: none; color: #007BFF; }\n')
        html_file.write('</style>\n')
        html_file.write('</head>\n<body>\n')
        html_file.write('<div class="sidebar">\n<h2>Navigation</h2>\n<ul>\n')

        # Create a list of links for each URL
        for index, result in enumerate(results):
            url = result.get("url", "N/A")
            html_file.write(f'<li><a href="#result-{index}">{url}</a></li>\n')

        html_file.write('</ul>\n</div>\n')
        html_file.write('<div class="content">\n<h1 id="results">🅿🅰🅶🅴🆂🆇🅲🆁🅰🆆🅻🅴🆁 Results</h1>\n')
        
        # Add search bar and filters
        html_file.write('''<div>
            <input type="text" id="searchInput" placeholder="Search by keyword..." onkeyup="filterResults()" style="padding: 5px; margin-bottom: 10px; width: 200px;">
            <select id="filterDropdown" onchange="filterResults()" style="padding: 5px; margin-left: 10px;">
                <option value="">Filter by depth</option>
                <option value="1">Depth 1</option>
                <option value="2">Depth 2</option>
                <option value="3">Depth 3</option>
                <!-- Add more depth options if needed -->
            </select>
        </div>''')

        # Add results container
        if results:
            html_file.write('<div class="results-container" id="resultsContainer">\n')
            for index, result in enumerate(results):
                url = result.get("url", "N/A")
                depth = result.get("depth", "N/A")
                title = result.get("title", "N/A")
                meta_description = result.get("meta_description", "N/A")
                meta_keywords = result.get("meta_keywords", "N/A")
                internal_link_count = result.get("internal_link_count", "0")
                external_link_count = result.get("external_link_count", "0")
                word_count = result.get("word_count", "0")
                image_count = result.get("image_count", "0")
                h1_tags = ', '.join(result.get("h1_tags", []))
                h2_tags = ', '.join(result.get("h2_tags", []))

                html_file.write(
                    f'<div class="result-card" id="result-{index}" data-depth="{depth}" data-keywords="{meta_keywords}">'
                    f'<h3 class="url">{url}</h3>'
                    f'<p><strong>Depth:</strong> {depth}</p>'
                    f'<p><strong>Title:</strong> {title}</p>'
                    f'<p><strong>Meta Description:</strong> {meta_description}</p>'
                    f'<p><strong>Meta Keywords:</strong> {meta_keywords}</p>'
                    f'<p><strong>H1 Tags:</strong> {h1_tags}</p>'
                    f'<p><strong>H2 Tags:</strong> {h2_tags}</p>'
                    f'<p><strong>Internal Links:</strong> {internal_link_count}</p>'
                    f'<p><strong>External Links:</strong> {external_link_count}</p>'
                    f'<p><strong>Word Count:</strong> {word_count}</p>'
                    f'<p><strong>Image Count:</strong> {image_count}</p>'
                    f'</div>\n'
                )
            html_file.write('</div>\n')
        else:
            html_file.write('<p>No crawl results available at the moment.</p>\n')

        # Add JavaScript for search and filter functionality
        html_file.write('''<script>
            function filterResults() {
                const searchInput = document.getElementById('searchInput').value.trim().toLowerCase();
                const filterDropdown = document.getElementById('filterDropdown').value;
                const resultsContainer = document.getElementById('resultsContainer');
                const resultCards = resultsContainer.getElementsByClassName('result-card');

                Array.from(resultCards).forEach(card => {
                    const keywords = card.getAttribute('data-keywords').toLowerCase();
                    const depth = card.getAttribute('data-depth');
                    const matchesSearch = !searchInput || keywords.includes(searchInput);
                    const matchesFilter = !filterDropdown || depth === filterDropdown;

                    if (matchesSearch && matchesFilter) {
                        card.style.display = 'block';
                    } else {
                        card.style.display = 'none';
                    }
                });
            }
        </script>''')

        # Footer and closing tags
        html_file.write('</div>\n</body>\n</html>')

if __name__ == "__main__":
    update_html()
