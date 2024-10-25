# This script contains unit tests for the web crawler.
# It ensures that the crawler functions as expected and handles various edge cases.

import unittest
from crawler import crawl

class TestCrawler(unittest.TestCase):

    def test_crawl_valid_url(self):
        results = crawl("https://example.com", 1)
        self.assertTrue(len(results) > 0)  # Check if at least one link is found

    def test_crawl_invalid_url(self):
        results = crawl("https://invalid-url.com", 1)
        self.assertEqual(results, [])  # No results should be found

if __name__ == "__main__":
    unittest.main()
