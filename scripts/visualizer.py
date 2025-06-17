import os
import json
import csv
import matplotlib.pyplot as plt
from PyPDF2 import PdfWriter, PdfReader
from io import BytesIO
from datetime import datetime
from collections import defaultdict
from urllib.parse import urlparse

# Configuration
VISUALIZATIONS_DIR = "visualizations"
DATA_DIR = "data"
os.makedirs(VISUALIZATIONS_DIR, exist_ok=True)

def load_data():
    """Load data from JSON and CSV files"""
    results = []
    
    json_path = os.path.join(DATA_DIR, 'results.json')
    csv_path = os.path.join(DATA_DIR, 'results.csv')
    
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            results.extend(json.load(f))
    
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                results.append(row)
    
    return results

def generate_charts(results):
    """Generate matplotlib charts from crawl data"""
    # Aggregate data for charts
    domains = defaultdict(int)
    word_counts = []
    image_counts = []
    internal_links = []
    external_links = []
    
    for result in results:
        domain = urlparse(result['url']).netloc
        domains[domain] += 1
        word_counts.append(int(result.get('word_count', 0)))
        image_counts.append(int(result.get('image_count', 0)))
        internal_links.append(int(result.get('internal_link_count', 0)))
        external_links.append(int(result.get('external_link_count', 0)))
    
    # Chart 1: Pages by Domain (Top 10)
    top_domains = sorted(domains.items(), key=lambda x: x[1], reverse=True)[:10]
    plt.figure(figsize=(10, 6))
    plt.barh([d[0] for d in top_domains], [d[1] for d in top_domains], color='indigo')
    plt.title('Top 10 Domains by Page Count')
    plt.xlabel('Number of Pages')
    plt.tight_layout()
    domains_chart = os.path.join(VISUALIZATIONS_DIR, 'domains_chart.png')
    plt.savefig(domains_chart)
    plt.close()
    
    # Chart 2: Word Count Distribution
    plt.figure(figsize=(10, 6))
    plt.hist(word_counts, bins=20, color='teal', edgecolor='black')
    plt.title('Distribution of Word Counts per Page')
    plt.xlabel('Word Count')
    plt.ylabel('Number of Pages')
    plt.tight_layout()
    words_chart = os.path.join(VISUALIZATIONS_DIR, 'words_chart.png')
    plt.savefig(words_chart)
    plt.close()
    
    # Chart 3: Internal vs External Links
    avg_int = sum(internal_links) / len(internal_links)
    avg_ext = sum(external_links) / len(external_links)
    plt.figure(figsize=(8, 6))
    plt.bar(['Internal Links', 'External Links'], [avg_int, avg_ext], color=['blue', 'orange'])
    plt.title('Average Links per Page')
    plt.ylabel('Number of Links')
    plt.tight_layout()
    links_chart = os.path.join(VISUALIZATIONS_DIR, 'links_chart.png')
    plt.savefig(links_chart)
    plt.close()
    
    return {
        'domains_chart': domains_chart,
        'words_chart': words_chart,
        'links_chart': links_chart
    }

def generate_pdf_report(chart_paths, run_id):
    """Generate a PDF report with visualizations"""
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    
    report_path = os.path.join(VISUALIZATIONS_DIR, f'report_{run_id}.pdf')
    doc = SimpleDocTemplate(report_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    story.append(Paragraph("Crawl Results Report", styles['Title']))
    story.append(Spacer(1, 0.25 * inch))
    
    # Date
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 0.5 * inch))
    
    # Charts
    story.append(Paragraph("Pages by Domain", styles['Heading2']))
    img = Image(chart_paths['domains_chart'], width=6*inch, height=3.6*inch)
    story.append(img)
    story.append(Spacer(1, 0.5 * inch))
    
    story.append(Paragraph("Word Count Distribution", styles['Heading2']))
    img = Image(chart_paths['words_chart'], width=6*inch, height=3.6*inch)
    story.append(img)
    story.append(Spacer(1, 0.5 * inch))
    
    story.append(Paragraph("Average Links per Page", styles['Heading2']))
    img = Image(chart_paths['links_chart'], width=6*inch, height=3.6*inch)
    story.append(img)
    
    doc.build(story)
    return report_path

def update_html_with_visualizations(chart_paths):
    """Update the HTML dashboard to include visualization references"""
    html_path = 'index.html'
    
    if not os.path.exists(html_path):
        return
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Add visualization section before the filter controls
    visualization_html = f"""
    <!-- Visualizations Section -->
    <div class="bg-white rounded-xl shadow-md p-6 mb-8">
        <h2 class="text-xl font-bold text-gray-800 mb-6">Data Visualizations</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
                <h3 class="text-lg font-semibold mb-2">Pages by Domain</h3>
                <img src="{chart_paths['domains_chart']}" alt="Domains Chart" class="w-full rounded-lg">
            </div>
            <div>
                <h3 class="text-lg font-semibold mb-2">Word Count Distribution</h3>
                <img src="{chart_paths['words_chart']}" alt="Words Chart" class="w-full rounded-lg">
            </div>
            <div class="md:col-span-2">
                <h3 class="text-lg font-semibold mb-2">Average Links per Page</h3>
                <img src="{chart_paths['links_chart']}" alt="Links Chart" class="w-full rounded-lg">
            </div>
        </div>
    </div>
    """
    
    # Insert after the Charts Section
    updated_html = html_content.replace(
        '<!-- Filter Controls -->',
        f'{visualization_html}\n<!-- Filter Controls -->'
    )
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(updated_html)

def main():
    # Get GitHub run ID if available
    run_id = os.getenv('GITHUB_RUN_ID', 'local')
    
    print("Loading crawl data...")
    results = load_data()
    
    if not results:
        print("No results found to visualize")
        return
    
    print("Generating charts...")
    chart_paths = generate_charts(results)
    
    print("Generating PDF report...")
    pdf_report = generate_pdf_report(chart_paths, run_id)
    
    print("Updating HTML dashboard...")
    update_html_with_visualizations(chart_paths)
    
    print(f"Visualization complete. Report saved to: {pdf_report}")

if __name__ == "__main__":
    main()
