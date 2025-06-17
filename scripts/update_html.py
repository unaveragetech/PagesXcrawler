import json
import os
import csv
from collections import defaultdict
from urllib.parse import urlparse
from html import escape
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

def calculate_averages(results):
    """Calculate average metrics across all pages"""
    if not results:
        return {}
    
    metrics = [
        'word_count', 'image_count', 'js_files_count', 'css_files_count',
        'internal_link_count', 'external_link_count', 'nofollow_link_count',
        'empty_anchor_text_count', 'keyword_rich_anchor_text_count'
    ]
    
    totals = {metric: 0 for metric in metrics}
    max_values = {metric: 0 for metric in metrics}
    
    for result in results:
        for metric in metrics:
            value = int(result.get(metric, 0))
            totals[metric] += value
            if value > max_values[metric]:
                max_values[metric] = value
    
    averages = {f'avg_{metric}': totals[metric] / len(results) for metric in metrics}
    averages.update({f'max_{metric}': max_values[metric] for metric in metrics})
    
    return averages

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
    total_js_files = 0
    total_css_files = 0
    total_fonts = 0
    total_videos = 0
    total_audios = 0
    total_internal_links = 0
    total_external_links = 0
    total_nofollow_links = 0
    total_empty_anchors = 0
    total_keyword_anchors = 0
    depths = set()

    for result in results:
        domain = urlparse(result['url']).netloc
        domains[domain] += 1
        if 'content_type' in result:
            content_type = result['content_type'].split(';')[0].strip()
            content_types[content_type] += 1

        # Count basic stats
        total_words += int(result.get('word_count', 0))
        total_images += int(result.get('image_count', 0))
        depths.add(int(result.get('depth', 0)))

        # Count resource stats
        total_js_files += int(result.get('js_files_count', 0))
        total_css_files += int(result.get('css_files_count', 0))
        total_fonts += int(result.get('font_count', 0))
        total_videos += int(result.get('video_count', 0))
        total_audios += int(result.get('audio_count', 0))

        # Count link stats
        total_internal_links += int(result.get('internal_link_count', 0))
        total_external_links += int(result.get('external_link_count', 0))
        total_nofollow_links += int(result.get('nofollow_link_count', 0))
        total_empty_anchors += int(result.get('empty_anchor_text_count', 0))
        total_keyword_anchors += int(result.get('keyword_rich_anchor_text_count', 0))

    # Calculate averages
    averages = calculate_averages(results)

    # Write HTML content
    with open('index.html', 'w', encoding='utf-8') as html_file:
        html_file.write(f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crawler Results Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
        }}
        .description-text {{
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}
        .chart-container {{
            height: 300px;
        }}
        @media (max-width: 768px) {{
            .chart-container {{
                height: 200px;
            }}
        }}
    </style>
</head>
<body class="bg-gray-50">
    <div class="min-h-screen">
        <!-- Header -->
        <header class="bg-indigo-600 text-white shadow-lg">
            <div class="container mx-auto px-4 py-6">
                <div class="flex flex-col md:flex-row justify-between items-center">
                    <div class="flex items-center mb-4 md:mb-0">
                        <i class="fas fa-spider text-2xl mr-3"></i>
                        <h1 class="text-2xl font-bold">Crawler Results Dashboard</h1>
                    </div>
                    <div class="w-full md:w-auto">
                        <div class="relative">
                            <input type="text" id="searchInput" placeholder="Search results..." 
                                   class="w-full md:w-64 px-4 py-2 rounded-lg bg-indigo-500 text-white placeholder-indigo-200 focus:outline-none focus:ring-2 focus:ring-indigo-300">
                            <i class="fas fa-search absolute right-3 top-3 text-indigo-200"></i>
                        </div>
                    </div>
                </div>
                <div class="mt-4 flex items-center text-sm">
                    <span class="bg-indigo-500 px-3 py-1 rounded-full mr-2">Last Updated:</span>
                    <span class="text-indigo-200">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
                </div>
            </div>
        </header>

        <!-- Main Content -->
        <main class="container mx-auto px-4 py-8">
            <!-- Summary Cards -->
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <div class="metric-card bg-white rounded-xl shadow-md p-6 transition-all duration-300">
                    <div class="flex items-center">
                        <div class="p-3 rounded-full bg-blue-100 text-blue-600 mr-4">
                            <i class="fas fa-file-alt text-xl"></i>
                        </div>
                        <div>
                            <p class="text-gray-500 text-sm">Total Pages</p>
                            <h3 class="text-2xl font-bold">{format_number(len(results))}</h3>
                        </div>
                    </div>
                </div>
                <div class="metric-card bg-white rounded-xl shadow-md p-6 transition-all duration-300">
                    <div class="flex items-center">
                        <div class="p-3 rounded-full bg-green-100 text-green-600 mr-4">
                            <i class="fas fa-link text-xl"></i>
                        </div>
                        <div>
                            <p class="text-gray-500 text-sm">Total Links</p>
                            <h3 class="text-2xl font-bold">{format_number(total_internal_links + total_external_links)}</h3>
                        </div>
                    </div>
                </div>
                <div class="metric-card bg-white rounded-xl shadow-md p-6 transition-all duration-300">
                    <div class="flex items-center">
                        <div class="p-3 rounded-full bg-purple-100 text-purple-600 mr-4">
                            <i class="fas fa-image text-xl"></i>
                        </div>
                        <div>
                            <p class="text-gray-500 text-sm">Total Images</p>
                            <h3 class="text-2xl font-bold">{format_number(total_images)}</h3>
                        </div>
                    </div>
                </div>
                <div class="metric-card bg-white rounded-xl shadow-md p-6 transition-all duration-300">
                    <div class="flex items-center">
                        <div class="p-3 rounded-full bg-yellow-100 text-yellow-600 mr-4">
                            <i class="fas fa-file-code text-xl"></i>
                        </div>
                        <div>
                            <p class="text-gray-500 text-sm">Total Assets</p>
                            <h3 class="text-2xl font-bold">{format_number(total_js_files + total_css_files + total_fonts + total_videos + total_audios)}</h3>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Charts Section -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                <div class="bg-white rounded-xl shadow-md p-6">
                    <h2 class="text-lg font-semibold mb-4 text-gray-800">Links Distribution</h2>
                    <div class="chart-container">
                        <canvas id="linksChart"></canvas>
                    </div>
                </div>
                <div class="bg-white rounded-xl shadow-md p-6">
                    <h2 class="text-lg font-semibold mb-4 text-gray-800">Content Metrics</h2>
                    <div class="chart-container">
                        <canvas id="contentChart"></canvas>
                    </div>
                </div>
            </div>

            <!-- Filter Controls -->
            <div class="bg-white rounded-xl shadow-md p-6 mb-8">
                <div class="flex flex-col md:flex-row justify-between items-center mb-6">
                    <h2 class="text-xl font-bold text-gray-800 mb-4 md:mb-0">Crawled Pages ({len(results)})</h2>
                    <div class="flex space-x-2">
                        <select id="domainFilter" class="px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-300">
                            <option value="">All Domains</option>''')

        # Add domain options
        for domain in sorted(domains):
            count = domains[domain]
            html_file.write(f'<option value="{escape(domain)}">{escape(domain)} ({format_number(count)})</option>')

        html_file.write('''
                        </select>
                        <select id="depthFilter" class="px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-300">
                            <option value="">All Depths</option>''')

        # Add depth options
        for depth in sorted(depths):
            html_file.write(f'<option value="{depth}">Depth {depth}</option>')

        html_file.write('''
                        </select>
                        <button id="filterButton" class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition">
                            <i class="fas fa-filter mr-2"></i> Filter
                        </button>
                    </div>
                </div>
                
                <!-- Results List -->
                <div id="resultsContainer" class="space-y-4">''')

        # Add result items
        for result in results:
            url = escape(result.get('url', 'N/A'))
            domain = escape(urlparse(url).netloc)
            depth = result.get('depth', 'N/A')
            title = escape(result.get('title', 'No Title'))
            word_count = int(result.get('word_count', 0))
            image_count = int(result.get('image_count', 0))
            internal_links = int(result.get('internal_link_count', 0))
            external_links = int(result.get('external_link_count', 0))
            url_length = int(result.get('url_length', 0))
            description = escape(result.get('meta_description', ''))
            status = 'Active'  # Default status, could be dynamic based on response code

            html_file.write(f'''
                    <div class="result-item border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition" data-domain="{domain}" data-depth="{depth}">
                        <div class="flex justify-between items-start mb-2">
                            <h3 class="font-semibold text-indigo-600">{title}</h3>
                            <span class="bg-green-100 text-green-800 text-xs px-2 py-1 rounded">{status}</span>
                        </div>
                        <a href="{url}" target="_blank" class="text-sm text-gray-500 block mb-2 truncate">{url}</a>
                        <p class="text-gray-600 description-text mb-3">
                            {description if description else 'No description available'}
                        </p>
                        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2 text-sm">
                            <div class="bg-gray-100 px-3 py-1 rounded">
                                <span class="font-medium">Words:</span> {format_number(word_count)}
                            </div>
                            <div class="bg-gray-100 px-3 py-1 rounded">
                                <span class="font-medium">Images:</span> {format_number(image_count)}
                            </div>
                            <div class="bg-gray-100 px-3 py-1 rounded">
                                <span class="font-medium">Int. Links:</span> {format_number(internal_links)}
                            </div>
                            <div class="bg-gray-100 px-3 py-1 rounded">
                                <span class="font-medium">Ext. Links:</span> {format_number(external_links)}
                            </div>
                            <div class="bg-gray-100 px-3 py-1 rounded">
                                <span class="font-medium">URL Length:</span> {format_number(url_length)}
                            </div>
                        </div>
                    </div>''')

        html_file.write('''
                </div>

                <!-- Pagination -->
                <div class="mt-6 flex justify-center">
                    <nav class="inline-flex rounded-md shadow">
                        <a href="#" class="px-3 py-2 rounded-l-md border border-gray-300 bg-white text-gray-500 hover:bg-gray-50">
                            <i class="fas fa-chevron-left"></i>
                        </a>
                        <a href="#" class="px-3 py-2 border-t border-b border-gray-300 bg-white text-gray-500 hover:bg-gray-50">1</a>
                        <a href="#" class="px-3 py-2 rounded-r-md border border-gray-300 bg-white text-gray-500 hover:bg-gray-50">
                            <i class="fas fa-chevron-right"></i>
                        </a>
                    </nav>
                </div>
            </div>
        </main>

        <!-- Footer -->
        <footer class="bg-gray-800 text-white py-8">
            <div class="container mx-auto px-4">
                <div class="flex flex-col md:flex-row justify-between items-center">
                    <div class="mb-4 md:mb-0">
                        <div class="flex items-center">
                            <i class="fas fa-spider text-xl mr-2"></i>
                            <span class="font-bold">Crawler Dashboard</span>
                        </div>
                        <p class="text-gray-400 text-sm mt-1">Analyze and visualize web crawler results</p>
                    </div>
                    <div class="flex space-x-4">
                        <a href="#" class="text-gray-400 hover:text-white">
                            <i class="fab fa-github text-xl"></i>
                        </a>
                    </div>
                </div>
                <div class="border-t border-gray-700 mt-6 pt-6 text-sm text-gray-400">
                    <p>© {datetime.now().year} Crawler Results Dashboard. All rights reserved.</p>
                </div>
            </div>
        </footer>
    </div>

    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        // Links Distribution Chart
        const linksCtx = document.getElementById('linksChart').getContext('2d');
        const linksChart = new Chart(linksCtx, {{
            type: 'doughnut',
            data: {{
                labels: ['Internal Links', 'External Links', 'Nofollow Links', 'Empty Anchors', 'Keyword Anchors'],
                datasets: [{{
                    data: [
                        {total_internal_links},
                        {total_external_links},
                        {total_nofollow_links},
                        {total_empty_anchors},
                        {total_keyword_anchors}
                    ],
                    backgroundColor: [
                        '#4F46E5',
                        '#10B981',
                        '#F59E0B',
                        '#EF4444',
                        '#8B5CF6'
                    ],
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'right',
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return `${{context.label}}: ${{context.raw.toLocaleString()}}`;
                            }}
                        }}
                    }}
                }}
            }}
        }});

        // Content Metrics Chart
        const contentCtx = document.getElementById('contentChart').getContext('2d');
        const contentChart = new Chart(contentCtx, {{
            type: 'bar',
            data: {{
                labels: ['Words', 'Images', 'JS Files', 'CSS Files'],
                datasets: [{{
                    label: 'Average per Page',
                    data: [
                        {averages.get('avg_word_count', 0):.0f},
                        {averages.get('avg_image_count', 0):.0f},
                        {averages.get('avg_js_files_count', 0):.0f},
                        {averages.get('avg_css_files_count', 0):.0f}
                    ],
                    backgroundColor: '#4F46E5',
                    borderRadius: 4
                }}, {{
                    label: 'Maximum',
                    data: [
                        {averages.get('max_word_count', 0)},
                        {averages.get('max_image_count', 0)},
                        {averages.get('max_js_files_count', 0)},
                        {averages.get('max_css_files_count', 0)}
                    ],
                    backgroundColor: '#8B5CF6',
                    borderRadius: 4
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{
                            callback: function(value) {{
                                return value.toLocaleString();
                            }}
                        }}
                    }}
                }},
                plugins: {{
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return `${{context.dataset.label}}: ${{context.raw.toLocaleString()}}`;
                            }}
                        }}
                    }}
                }}
            }}
        }});

        // Filter functionality
        function filterResults() {{
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const domainFilter = document.getElementById('domainFilter').value;
            const depthFilter = document.getElementById('depthFilter').value;
            const items = document.querySelectorAll('.result-item');

            items.forEach(item => {{
                const textContent = item.textContent.toLowerCase();
                const domain = item.getAttribute('data-domain');
                const depth = item.getAttribute('data-depth');

                const matchesSearch = searchTerm === '' || textContent.includes(searchTerm);
                const matchesDomain = domainFilter === '' || domain === domainFilter;
                const matchesDepth = depthFilter === '' || depth === depthFilter;

                if (matchesSearch && matchesDomain && matchesDepth) {{
                    item.style.display = 'block';
                }} else {{
                    item.style.display = 'none';
                }}
            }});
        }}

        document.getElementById('searchInput').addEventListener('input', filterResults);
        document.getElementById('filterButton').addEventListener('click', filterResults);

        // Toggle description text
        document.querySelectorAll('.description-text').forEach(el => {{
            el.addEventListener('click', function() {{
                this.classList.toggle('-webkit-line-clamp-3');
                this.classList.toggle('line-clamp-none');
            }});
        }});
    </script>
</body>
</html>''')

if __name__ == "__main__":
    update_html()
