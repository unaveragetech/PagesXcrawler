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
        html_file.write('<title>Web Crawler Results</title>\n')
        html_file.write('<style>\n')
        html_file.write('body { font-family: Arial, sans-serif; margin: 20px; }\n')
        html_file.write('h1 { color: #333; }\n')
        html_file.write('.results-container { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 10px; }\n')
        html_file.write('.result-card { border: 1px solid #ddd; border-radius: 8px; padding: 15px; background-color: #f9f9f9; }\n')
        html_file.write('.result-card h3 { font-size: 18px; }\n')
        html_file.write('.result-card p { margin: 5px 0; font-size: 14px; }\n')
        html_file.write('.url { font-weight: bold; color: #007BFF; }\n')
        html_file.write('</style>\n')
        html_file.write('</head>\n<body>\n')
        html_file.write('<h1>Web Crawler Results</h1>\n')
        
        if results:
            html_file.write('<div class="results-container">\n')
            for result in results:
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
                    f'<div class="result-card">'
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

        # Footer and closing tags
        html_file.write('</body>\n</html>')

if __name__ == "__main__":
    update_html()
