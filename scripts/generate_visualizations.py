import os
import json
import csv
import matplotlib.pyplot as plt
from collections import defaultdict
from urllib.parse import urlparse
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

# Directories
DATA_DIR = "data"
VIS_DIR = "visualizations"
ARCHIVE_DIR = os.path.join(DATA_DIR, "archive")
os.makedirs(VIS_DIR, exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)

def load_data():
    """Load and unify crawl data from JSON and CSV."""
    combined = []
    seen_urls = set()

    json_file = os.path.join(DATA_DIR, "results.json")
    csv_file = os.path.join(DATA_DIR, "results.csv")

    # Load JSON
    if os.path.exists(json_file):
        with open(json_file, "r", encoding="utf-8") as f:
            try:
                for row in json.load(f):
                    if isinstance(row, dict) and row.get("url") not in seen_urls:
                        combined.append(row)
                        seen_urls.add(row["url"])
            except Exception as e:
                print(f"Failed to load JSON: {e}")

    # Load CSV
    if os.path.exists(csv_file):
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("url") and row["url"] not in seen_urls:
                    combined.append(row)
                    seen_urls.add(row["url"])

    return combined

def generate_charts(results):
    """Generate and return paths to all charts."""
    domains = defaultdict(int)
    word_counts = []
    image_counts = []
    internal_links = []
    external_links = []

    for entry in results:
        url = entry.get("url", "")
        domain = urlparse(url).netloc or "unknown"
        domains[domain] += 1

        word_counts.append(int(entry.get("word_count", 0)))
        image_counts.append(int(entry.get("image_count", 0)))
        internal_links.append(int(entry.get("internal_link_count", 0)))
        external_links.append(int(entry.get("external_link_count", 0)))

    chart_paths = {}

    # Chart: Top Domains
    plt.figure(figsize=(10, 6))
    top_domains = sorted(domains.items(), key=lambda x: x[1], reverse=True)[:10]
    labels, values = zip(*top_domains) if top_domains else ([], [])
    plt.barh(labels, values, color="steelblue")
    plt.title("Top 10 Domains by Page Count")
    plt.xlabel("Pages")
    plt.tight_layout()
    domain_chart = os.path.join(VIS_DIR, "domains_chart.png")
    plt.savefig(domain_chart)
    plt.close()
    chart_paths["domains_chart"] = domain_chart

    # Chart: Word Count Histogram
    plt.figure(figsize=(10, 6))
    plt.hist(word_counts, bins=20, color="seagreen", edgecolor="black")
    plt.title("Distribution of Word Counts per Page")
    plt.xlabel("Word Count")
    plt.ylabel("Page Frequency")
    plt.tight_layout()
    word_chart = os.path.join(VIS_DIR, "words_chart.png")
    plt.savefig(word_chart)
    plt.close()
    chart_paths["words_chart"] = word_chart

    # Chart: Average Link Counts
    plt.figure(figsize=(8, 6))
    avg_internal = sum(internal_links) / len(internal_links) if internal_links else 0
    avg_external = sum(external_links) / len(external_links) if external_links else 0
    plt.bar(["Internal Links", "External Links"], [avg_internal, avg_external], color=["dodgerblue", "orange"])
    plt.title("Average Links per Page")
    plt.tight_layout()
    link_chart = os.path.join(VIS_DIR, "links_chart.png")
    plt.savefig(link_chart)
    plt.close()
    chart_paths["links_chart"] = link_chart

    return chart_paths

def generate_pdf_report(chart_paths, run_id):
    """Generate a PDF with all charts."""
    report_path = os.path.join(VIS_DIR, f"report_{run_id}.pdf")
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(report_path, pagesize=letter)
    story = [
        Paragraph("📄 Crawl Results Report", styles["Title"]),
        Spacer(1, 0.3 * inch),
        Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]),
        Spacer(1, 0.5 * inch),
    ]

    for label, img_file, title in [
        ("domains_chart", chart_paths.get("domains_chart"), "Pages by Domain"),
        ("words_chart", chart_paths.get("words_chart"), "Word Count Distribution"),
        ("links_chart", chart_paths.get("links_chart"), "Average Links per Page"),
    ]:
        if img_file and os.path.exists(img_file):
            story.append(Paragraph(title, styles["Heading2"]))
            story.append(Image(img_file, width=6 * inch, height=3.6 * inch))
            story.append(Spacer(1, 0.4 * inch))

    doc.build(story)
    return report_path

def update_html_with_visualizations(chart_paths):
    """Insert charts into the index.html dashboard."""
    html_path = "index.html"
    if not os.path.exists(html_path):
        print("No HTML dashboard to update.")
        return

    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Inject visualizations above the filter controls
    html_block = f"""
<!-- Visualizations Section -->
<div class="bg-white rounded-xl shadow-md p-6 mb-8">
  <h2 class="text-xl font-bold text-gray-800 mb-6">📊 Data Visualizations</h2>
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
<!-- End Visualizations Section -->
"""

    if "<!-- Filter Controls -->" in content:
        content = content.replace("<!-- Filter Controls -->", html_block + "\n<!-- Filter Controls -->")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ HTML dashboard updated.")
    else:
        print("⚠️ Could not insert visualizations. Marker not found.")

def main():
    run_id = os.getenv("GITHUB_RUN_ID", "local")
    print("📥 Loading crawl data...")
    data = load_data()

    if not data:
        print("❌ No crawl data found. Exiting.")
        return

    print("📊 Generating charts...")
    charts = generate_charts(data)

    print("📝 Creating PDF report...")
    report = generate_pdf_report(charts, run_id)

    print("🌐 Updating HTML dashboard...")
    update_html_with_visualizations(charts)

    print(f"✅ Done! PDF saved to: {report}")

if __name__ == "__main__":
    main()
