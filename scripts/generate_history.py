"""
Generate past_crawls.html – a page listing all past crawls and a how-to-use guide.

Data sources:
  data/history/crawl_history.csv  – columns: timestamp, url, depth, max_pages, pages_crawled, status
  data/issues_status.csv          – legacy history, variable format
"""

import os
import csv
import re
from html import escape
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, 'data')
HISTORY_CSV = os.path.join(DATA_DIR, 'history', 'crawl_history.csv')
ISSUES_CSV  = os.path.join(DATA_DIR, 'issues_status.csv')
OUT_PATH    = os.path.join(BASE_DIR, 'past_crawls.html')


def load_history():
    """Return a list of dicts with keys: timestamp, url, depth, max_pages, pages_crawled, status."""
    rows = []

    # --- primary history CSV ---
    if os.path.exists(HISTORY_CSV):
        try:
            with open(HISTORY_CSV, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if not row or row[0].startswith('#'):
                        continue
                    # Columns (no header): timestamp, url, depth, max_pages, pages_crawled, status
                    rows.append({
                        'timestamp':     (row[0] if len(row) > 0 else '').strip(),
                        'url':           (row[1] if len(row) > 1 else '').strip(),
                        'depth':         (row[2] if len(row) > 2 else '').strip(),
                        'max_pages':     (row[3] if len(row) > 3 else '').strip(),
                        'pages_crawled': (row[4] if len(row) > 4 else '').strip(),
                        'status':        (row[5] if len(row) > 5 else 'completed').strip(),
                    })
        except Exception as e:
            print(f"Warning: could not read {HISTORY_CSV}: {e}")

    # --- legacy issues_status.csv (best-effort) ---
    if os.path.exists(ISSUES_CSV):
        try:
            with open(ISSUES_CSV, 'r', encoding='utf-8') as f:
                lines = f.read().splitlines()

            for line in lines:
                line = line.strip()
                if not line or line.startswith('(') or line.startswith('#'):
                    continue
                # Try to extract a URL from the line
                url_match = re.search(r'https?://[^\s,]+', line)
                if not url_match:
                    continue
                url = url_match.group(0)

                # Depth
                depth_match = re.search(r':depth\((\d+)\)|,(\d+),|:(\d+),', line)
                depth = ''
                if depth_match:
                    depth = next(g for g in depth_match.groups() if g is not None)

                # Status
                status = 'completed' if 'completed' in line.lower() else 'unknown'

                rows.append({
                    'timestamp':     '',
                    'url':           url,
                    'depth':         depth,
                    'max_pages':     '',
                    'pages_crawled': '',
                    'status':        status,
                })
        except Exception as e:
            print(f"Warning: could not read {ISSUES_CSV}: {e}")

    return rows


def status_badge(status: str) -> str:
    s = (status or '').lower()
    if s == 'completed':
        return '<span class="bg-green-100 text-green-800 text-xs px-2 py-1 rounded font-medium">✓ completed</span>'
    if s in ('failed', 'error'):
        return '<span class="bg-red-100 text-red-800 text-xs px-2 py-1 rounded font-medium">✗ failed</span>'
    return f'<span class="bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded font-medium">{escape(status)}</span>'


def generate_history_html(rows: list) -> None:
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    total = len(rows)

    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        f.write(f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PagesXcrawler – Past Crawls &amp; How To Use</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        pre {{ background:#1e293b; color:#e2e8f0; border-radius:0.5rem; padding:1rem; overflow-x:auto; }}
        code {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size:0.85rem; }}
    </style>
</head>
<body class="bg-gray-50">
<div class="min-h-screen">

    <!-- Header -->
    <header class="bg-indigo-600 text-white shadow-lg">
        <div class="container mx-auto px-4 py-6">
            <div class="flex flex-col md:flex-row justify-between items-center gap-4">
                <div class="flex items-center gap-3">
                    <i class="fas fa-spider text-2xl"></i>
                    <h1 class="text-2xl font-bold">PagesXcrawler – Past Crawls</h1>
                </div>
                <nav class="flex gap-3 flex-wrap justify-center">
                    <a href="index.html"
                       class="flex items-center gap-1 bg-indigo-500 hover:bg-indigo-400 px-3 py-1.5 rounded-lg text-sm font-medium transition">
                        <i class="fas fa-chart-bar"></i> Results Dashboard
                    </a>
                    <a href="https://github.com/unaveragetech/PagesXcrawler/issues/new"
                       target="_blank"
                       class="flex items-center gap-1 bg-indigo-500 hover:bg-indigo-400 px-3 py-1.5 rounded-lg text-sm font-medium transition">
                        <i class="fas fa-plus"></i> New Crawl
                    </a>
                </nav>
            </div>
            <div class="mt-3 text-sm text-indigo-200">
                Last updated: {now} &nbsp;·&nbsp; {total} recorded crawl(s)
            </div>
        </div>
    </header>

    <main class="container mx-auto px-4 py-8 space-y-10">

        <!-- ── How To Use ───────────────────────────────────────────── -->
        <section class="bg-white rounded-xl shadow-md p-6">
            <h2 class="text-2xl font-bold text-gray-800 mb-4">
                <i class="fas fa-book-open text-indigo-500 mr-2"></i>How to Use PagesXcrawler
            </h2>
            <p class="text-gray-600 mb-4">
                PagesXcrawler is a GitHub-powered web crawler.  Every crawl is triggered by
                a GitHub Issue or the Actions workflow dispatch UI, and results are published
                automatically to this GitHub Pages site.
            </p>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">

                <!-- Method 1 -->
                <div class="border border-indigo-100 rounded-xl p-5 bg-indigo-50">
                    <h3 class="text-lg font-semibold text-indigo-700 mb-2">
                        <i class="fas fa-ticket-alt mr-1"></i> Method 1 – GitHub Issue
                    </h3>
                    <ol class="list-decimal list-inside text-gray-700 space-y-1 text-sm">
                        <li>Go to the
                            <a href="https://github.com/unaveragetech/PagesXcrawler/issues/new"
                               target="_blank" class="text-indigo-600 underline">Issues tab</a>
                            and click <strong>New issue</strong>.
                        </li>
                        <li>Set the <strong>title</strong> using the format below and submit.</li>
                        <li>The bot will comment with progress and close the issue when done.</li>
                    </ol>
                    <pre class="mt-3"><code>crawl: https://example.com 3
crawl: https://example.com 2 --max-pages 50 --timeout 15</code></pre>
                </div>

                <!-- Method 2 -->
                <div class="border border-green-100 rounded-xl p-5 bg-green-50">
                    <h3 class="text-lg font-semibold text-green-700 mb-2">
                        <i class="fas fa-play-circle mr-1"></i> Method 2 – Workflow Dispatch
                    </h3>
                    <ol class="list-decimal list-inside text-gray-700 space-y-1 text-sm">
                        <li>Go to
                            <a href="https://github.com/unaveragetech/PagesXcrawler/actions/workflows/crawler.yml"
                               target="_blank" class="text-green-600 underline">Actions → Web Crawler</a>.
                        </li>
                        <li>Click <strong>Run workflow</strong> and fill in the fields.</li>
                        <li>The results dashboard will update automatically after the run.</li>
                    </ol>
                    <pre class="mt-3"><code># fields available:
URL          – e.g. https://example.com
DEPTH        – e.g. 3
MAX_PAGES    – e.g. 100   (default)
TIMEOUT      – e.g. 10    (seconds, default)
ROTATE_AGENT – e.g. 10   (requests before agent rotation)</code></pre>
                </div>
            </div>

            <!-- Parameters table -->
            <h3 class="text-lg font-semibold text-gray-800 mb-2">Command-Line / Issue Parameters</h3>
            <div class="overflow-x-auto">
                <table class="w-full text-sm text-left border-collapse">
                    <thead>
                        <tr class="bg-gray-100">
                            <th class="px-4 py-2 border border-gray-200 font-semibold">Parameter</th>
                            <th class="px-4 py-2 border border-gray-200 font-semibold">Required</th>
                            <th class="px-4 py-2 border border-gray-200 font-semibold">Default</th>
                            <th class="px-4 py-2 border border-gray-200 font-semibold">Description</th>
                        </tr>
                    </thead>
                    <tbody class="text-gray-700">
                        <tr class="hover:bg-gray-50">
                            <td class="px-4 py-2 border border-gray-200 font-mono">url</td>
                            <td class="px-4 py-2 border border-gray-200">✅</td>
                            <td class="px-4 py-2 border border-gray-200">—</td>
                            <td class="px-4 py-2 border border-gray-200">The URL to crawl (must start with http:// or https://)</td>
                        </tr>
                        <tr class="hover:bg-gray-50">
                            <td class="px-4 py-2 border border-gray-200 font-mono">depth</td>
                            <td class="px-4 py-2 border border-gray-200">✅</td>
                            <td class="px-4 py-2 border border-gray-200">—</td>
                            <td class="px-4 py-2 border border-gray-200">Number of link levels to follow (1–5 recommended)</td>
                        </tr>
                        <tr class="hover:bg-gray-50">
                            <td class="px-4 py-2 border border-gray-200 font-mono">--max-pages</td>
                            <td class="px-4 py-2 border border-gray-200">❌</td>
                            <td class="px-4 py-2 border border-gray-200">100</td>
                            <td class="px-4 py-2 border border-gray-200">Maximum pages to crawl</td>
                        </tr>
                        <tr class="hover:bg-gray-50">
                            <td class="px-4 py-2 border border-gray-200 font-mono">--timeout</td>
                            <td class="px-4 py-2 border border-gray-200">❌</td>
                            <td class="px-4 py-2 border border-gray-200">10</td>
                            <td class="px-4 py-2 border border-gray-200">Per-request timeout in seconds</td>
                        </tr>
                        <tr class="hover:bg-gray-50">
                            <td class="px-4 py-2 border border-gray-200 font-mono">--rotate-agent-after</td>
                            <td class="px-4 py-2 border border-gray-200">❌</td>
                            <td class="px-4 py-2 border border-gray-200">10</td>
                            <td class="px-4 py-2 border border-gray-200">Requests between user-agent rotations</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </section>

        <!-- ── Past Crawls Table ─────────────────────────────────────── -->
        <section class="bg-white rounded-xl shadow-md p-6">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between mb-4 gap-2">
                <h2 class="text-2xl font-bold text-gray-800">
                    <i class="fas fa-history text-indigo-500 mr-2"></i>Past Crawls ({total})
                </h2>
                <input type="text" id="historySearch" placeholder="Search…"
                       class="px-3 py-2 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 w-full sm:w-56">
            </div>
            <div class="overflow-x-auto">
                <table class="w-full text-sm text-left border-collapse" id="historyTable">
                    <thead>
                        <tr class="bg-gray-100 text-gray-600 uppercase text-xs">
                            <th class="px-4 py-3 border border-gray-200">#</th>
                            <th class="px-4 py-3 border border-gray-200">Timestamp</th>
                            <th class="px-4 py-3 border border-gray-200">URL</th>
                            <th class="px-4 py-3 border border-gray-200 text-center">Depth</th>
                            <th class="px-4 py-3 border border-gray-200 text-center">Max Pages</th>
                            <th class="px-4 py-3 border border-gray-200 text-center">Pages Crawled</th>
                            <th class="px-4 py-3 border border-gray-200 text-center">Status</th>
                        </tr>
                    </thead>
                    <tbody class="text-gray-700">
''')

        if rows:
            for i, row in enumerate(reversed(rows), 1):
                ts   = escape(row.get('timestamp', ''))
                url  = escape(row.get('url', ''))
                dep  = escape(row.get('depth', ''))
                mxp  = escape(row.get('max_pages', ''))
                pgc  = escape(row.get('pages_crawled', ''))
                st   = row.get('status', '')
                badge = status_badge(st)
                f.write(f'''                        <tr class="hover:bg-gray-50 history-row">
                            <td class="px-4 py-2 border border-gray-200 text-gray-400">{i}</td>
                            <td class="px-4 py-2 border border-gray-200 whitespace-nowrap">{ts}</td>
                            <td class="px-4 py-2 border border-gray-200 max-w-xs">
                                <a href="{url}" target="_blank"
                                   class="text-indigo-600 hover:underline truncate block max-w-xs"
                                   title="{url}">{url}</a>
                            </td>
                            <td class="px-4 py-2 border border-gray-200 text-center">{dep}</td>
                            <td class="px-4 py-2 border border-gray-200 text-center">{mxp}</td>
                            <td class="px-4 py-2 border border-gray-200 text-center">{pgc}</td>
                            <td class="px-4 py-2 border border-gray-200 text-center">{badge}</td>
                        </tr>\n''')
        else:
            f.write('''                        <tr>
                            <td colspan="7" class="px-4 py-8 text-center text-gray-400">
                                No crawl history found yet. Run your first crawl!
                            </td>
                        </tr>\n''')

        f.write(f'''                    </tbody>
                </table>
            </div>
            <p class="mt-3 text-xs text-gray-400">Rows are shown newest-first.</p>
        </section>

    </main>

    <!-- Footer -->
    <footer class="bg-gray-800 text-white py-8 mt-4">
        <div class="container mx-auto px-4">
            <div class="flex flex-col md:flex-row justify-between items-center gap-4">
                <div>
                    <div class="flex items-center gap-2">
                        <i class="fas fa-spider text-xl"></i>
                        <span class="font-bold">PagesXcrawler</span>
                    </div>
                    <p class="text-gray-400 text-sm mt-1">Automated web crawling with GitHub Actions</p>
                </div>
                <div class="flex gap-4 items-center">
                    <a href="index.html" class="text-gray-400 hover:text-white text-sm">
                        <i class="fas fa-chart-bar mr-1"></i>Dashboard
                    </a>
                    <a href="https://github.com/unaveragetech/PagesXcrawler" target="_blank"
                       class="text-gray-400 hover:text-white">
                        <i class="fab fa-github text-xl"></i>
                    </a>
                </div>
            </div>
            <div class="border-t border-gray-700 mt-6 pt-6 text-sm text-gray-400">
                <p>© {datetime.now().year} PagesXcrawler. All rights reserved.</p>
            </div>
        </div>
    </footer>
</div>

<script>
    const searchInput = document.getElementById('historySearch');
    searchInput.addEventListener('input', function() {{
        const q = this.value.toLowerCase();
        document.querySelectorAll('.history-row').forEach(row => {{
            row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
        }});
    }});
</script>
</body>
</html>
''')

    print(f"Generated {OUT_PATH} with {total} crawl record(s).")


def main():
    rows = load_history()
    generate_history_html(rows)


if __name__ == '__main__':
    main()
