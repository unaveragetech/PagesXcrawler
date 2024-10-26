# This script updates the `index.html` file with the latest results from `results.json` and `results.csv`.
# It processes the data and formats it appropriately for display on the GitHub Pages site.

import json
import os

def update_html():
    json_path = 'data/results.json'
    if os.path.exists(json_path):
        with open(json_path, 'r') as json_file:
            data = json.load(json_file)
        
        with open('index.html', 'w') as html_file:
            html_file.write('<!DOCTYPE html>\n<html lang="en">\n<head>\n')
            html_file.write('<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n')
            html_file.write('<title>Web Crawler Results</title>\n</head>\n<body>\n')
            html_file.write('<h1>Web Crawler Results</h1>\n<div id="results">\n')
            for result in data:
                html_file.write(f'<div>URL: {result["url"]}, Depth: {result["depth"]}</div>\n')
            html_file.write('</div>\n</body>\n</html>')

if __name__ == "__main__":
    update_html()
