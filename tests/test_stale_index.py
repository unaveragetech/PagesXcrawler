"""Tests that verify the stale-index-entry fix.

The core bug was:
  1. save_results() skipped writing results.csv when results=[],
     leaving behind stale CSV data from the previous crawl.
  2. load_results() (update_html) and load_data() (generate_visualizations)
     merged JSON + CSV, so the stale CSV entries appeared in the dashboard
     even after a new (empty) crawl completed.

Fixes:
  - save_results() always writes (or clears) results.csv.
  - load_results() / load_data() treat JSON as the sole authoritative source
    and only fall back to CSV when JSON is missing or unreadable.
"""

import csv
import json
import os
import sys
import tempfile
import unittest

# Allow importing from the scripts/ directory and the repo root
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SCRIPTS_DIR = os.path.join(REPO_ROOT, 'scripts')
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, SCRIPTS_DIR)

import update_html  # scripts/update_html.py
import generate_visualizations  # scripts/generate_visualizations.py


class TestSaveResultsClearsCSV(unittest.TestCase):
    """save_results() must always write or clear results.csv."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self._orig_cwd = os.getcwd()
        os.chdir(self.tmpdir)
        os.makedirs('data', exist_ok=True)

    def tearDown(self):
        os.chdir(self._orig_cwd)

    def _make_result(self, url='https://example.com', title='Test'):
        """Return a minimal crawl result dict."""
        return {
            'url': url, 'depth': 0, 'title': title,
            'meta_description': '', 'meta_keywords': '', 'favicon': '',
            'canonical_url': '', 'og_title': '', 'og_description': '',
            'og_image': '', 'url_length': len(url), 'url_params_count': 0,
            'url_path_depth': 0, 'internal_link_count': 0,
            'external_link_count': 0, 'nofollow_link_count': 0,
            'empty_anchor_text_count': 0, 'generic_anchor_text_count': 0,
            'keyword_rich_anchor_text_count': 0, 'internal_external_ratio': 0,
            'total_link_count': 0, 'js_files_count': 0, 'css_files_count': 0,
            'image_count': 0, 'font_count': 0, 'video_count': 0,
            'audio_count': 0, 'internal_resources_count': 0,
            'external_resources_count': 0, 'word_count': 10,
            'content_size': 100, 'crawl_timestamp': '2026-01-01T00:00:00',
            'status_code': 200,
        }

    def test_csv_cleared_when_results_empty(self):
        """After a crawl with empty results, results.csv must be empty (not stale)."""
        from crawler import save_results

        # Simulate a previous crawl that populated the CSV
        stale = self._make_result('https://stale.example.com', 'Stale')
        save_results([stale])
        with open('data/results.csv', 'r') as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 1, "CSV should have one stale row before the new crawl")

        # New crawl returns nothing — CSV must be cleared
        save_results([])
        with open('data/results.csv', 'r') as f:
            content = f.read()
        self.assertEqual(content, '', "CSV must be empty after a crawl with no results")

    def test_csv_written_when_results_nonempty(self):
        """results.csv is written correctly when results are non-empty."""
        from crawler import save_results

        result = self._make_result()
        save_results([result])
        with open('data/results.csv', 'r') as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['url'], 'https://example.com')


class TestLoadResultsNoStaleCSV(unittest.TestCase):
    """load_results() must not return stale CSV data when JSON is available."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.json_path = os.path.join(self.tmpdir, 'results.json')
        self.csv_path = os.path.join(self.tmpdir, 'results.csv')

    def _write_stale_csv(self, url='https://stale.example.com'):
        with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['url', 'title'])
            writer.writeheader()
            writer.writerow({'url': url, 'title': 'Stale'})

    def test_empty_json_does_not_return_stale_csv(self):
        """When JSON is [] (empty crawl), stale CSV entries must NOT be returned."""
        with open(self.json_path, 'w') as f:
            json.dump([], f)
        self._write_stale_csv()

        results = update_html.load_results(self.json_path, self.csv_path)
        self.assertEqual(results, [], "Stale CSV entries must not appear when JSON is empty")

    def test_fresh_json_is_used_not_stale_csv(self):
        """When JSON has fresh data, only those entries should be returned."""
        fresh = [{'url': 'https://fresh.example.com', 'title': 'Fresh'}]
        with open(self.json_path, 'w') as f:
            json.dump(fresh, f)
        self._write_stale_csv('https://stale.example.com')

        results = update_html.load_results(self.json_path, self.csv_path)
        urls = [r['url'] for r in results]
        self.assertIn('https://fresh.example.com', urls)
        self.assertNotIn('https://stale.example.com', urls,
                         "Stale CSV URL must not appear when JSON has data")

    def test_csv_fallback_when_json_missing(self):
        """When JSON does not exist, CSV data is used as a fallback."""
        self._write_stale_csv('https://csv-only.example.com')
        # Do NOT create a JSON file

        results = update_html.load_results(self.json_path, self.csv_path)
        urls = [r['url'] for r in results]
        self.assertIn('https://csv-only.example.com', urls)

    def test_csv_fallback_when_json_corrupt(self):
        """When JSON is corrupt, CSV data is used as a fallback."""
        with open(self.json_path, 'w') as f:
            f.write("not valid json{{{{")
        self._write_stale_csv('https://csv-only.example.com')

        results = update_html.load_results(self.json_path, self.csv_path)
        urls = [r['url'] for r in results]
        self.assertIn('https://csv-only.example.com', urls)


class TestLoadDataNoStaleCSV(unittest.TestCase):
    """generate_visualizations.load_data() must not return stale CSV data when JSON exists."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        # Patch DATA_DIR in the module
        self._orig_data_dir = generate_visualizations.DATA_DIR
        generate_visualizations.DATA_DIR = self.tmpdir

    def tearDown(self):
        generate_visualizations.DATA_DIR = self._orig_data_dir

    def _write_json(self, data):
        with open(os.path.join(self.tmpdir, 'results.json'), 'w') as f:
            json.dump(data, f)

    def _write_stale_csv(self, url='https://stale.example.com'):
        with open(os.path.join(self.tmpdir, 'results.csv'), 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['url', 'title'])
            writer.writeheader()
            writer.writerow({'url': url, 'title': 'Stale'})

    def test_empty_json_does_not_return_stale_csv(self):
        self._write_json([])
        self._write_stale_csv()

        data = generate_visualizations.load_data()
        self.assertEqual(data, [], "Stale CSV entries must not appear when JSON is empty")

    def test_fresh_json_excludes_stale_csv(self):
        fresh = [{'url': 'https://fresh.example.com', 'title': 'Fresh'}]
        self._write_json(fresh)
        self._write_stale_csv('https://stale.example.com')

        data = generate_visualizations.load_data()
        urls = [r['url'] for r in data]
        self.assertIn('https://fresh.example.com', urls)
        self.assertNotIn('https://stale.example.com', urls)

    def test_csv_fallback_when_json_missing(self):
        self._write_stale_csv('https://csv-only.example.com')

        data = generate_visualizations.load_data()
        urls = [r['url'] for r in data]
        self.assertIn('https://csv-only.example.com', urls)


if __name__ == '__main__':
    unittest.main()
