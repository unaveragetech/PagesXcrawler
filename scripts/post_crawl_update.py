"""Run this after a crawl finishes to regenerate the dashboard and visualizations.

Usage: python post_crawl_update.py

This will:
 - run update_html.update_html() to (re)generate the root `index.html` from data
 - run generate_visualizations.main() to create charts and inject them into the root `index.html`
"""

import sys
import update_html
import generate_visualizations


def main():
    try:
        print("Running HTML updater...")
        update_html.update_html()
    except Exception as e:
        print(f"Updater failed: {e}")

    try:
        print("Generating visualizations and updating HTML...")
        generate_visualizations.main()
    except Exception as e:
        print(f"Visualizations failed: {e}")
        return 1

    print("Post-crawl update completed.")
    return 0


if __name__ == '__main__':
    sys.exit(main())