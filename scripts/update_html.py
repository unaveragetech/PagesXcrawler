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
        html_file.write('#results-table { width: 100%; border-collapse: collapse; }\n')
        html_file.write('th, td { padding: 10px; border: 1px solid #ddd; text-align: left; }\n')
        html_file.write('th { background-color: #f4f4f4; }\n')
        html_file.write('</style>\n')
        html_file.write('</head>\n<body>\n')
        html_file.write('<h1>Web Crawler Results</h1>\n')
        
        if results:
            # Create table to display results
            html_file.write('<table id="results-table">\n')
            html_file.write('<tr><th>URL</th><th>Depth</th><th>Title</th><th>Status</th><th>Date Crawled</th></tr>\n')
            
            for result in results:
                url = result.get("url", "N/A")
                depth = result.get("depth", "N/A")
                title = result.get("title", "N/A")
                status = result.get("status", "Pending")
                date_crawled = result.get("date_crawled", "N/A")

                html_file.write(f'<tr><td>{url}</td><td>{depth}</td><td>{title}</td><td>{status}</td><td>{date_crawled}</td></tr>\n')
            
            html_file.write('</table>\n')
        else:
            html_file.write('<p>No crawl results available at the moment.</p>\n')

        # Footer and closing tags
        html_file.write('</body>\n</html>')

if __name__ == "__main__":
    update_html()
