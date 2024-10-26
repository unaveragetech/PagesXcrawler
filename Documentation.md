
🌐 Introducing PagesXcrawler: My New Proof-of-Concept Web Crawler! 🌐

Ever wanted a way to explore a website from top to bottom without needing to be an expert in web scraping? That’s exactly why I made PagesXcrawler—a simple, self-hosted, and straightforward web crawler that requires no setup and minimal knowledge to get started. It was a proof of concept at first, but it turned out to be a powerful and useful tool for diving deep into sites, gathering all the links you need in one go. Here’s why it’s awesome and how it works!

Why PagesXcrawler?

Building PagesXcrawler was about showing that crawling a website doesn’t have to be complicated or require a complex setup. The idea was to take something typically reserved for developers or data scientists and make it accessible to anyone with a GitHub account. Now, with just a few clicks and a tiny bit of typing, you can gather all the links from a website at any level of depth, making it perfect for SEO, research, or just seeing where a site’s rabbit hole takes you.

Imagine wanting to see how deeply Wikipedia branches out, or mapping a blog’s internal links. You could do this with expensive software or a programming background—or you could just use PagesXcrawler!

How to Use PagesXcrawler (Super Simple Steps):

	1.	Head to the PagesXcrawler Repo: Everything is hosted on GitHub, so there’s no software to download, and it’s free to use.
	2.	Create a New Issue with Your Target Link: In the repo, open a new issue and, in the title, paste the link you want to crawl. Add a colon and then the crawl depth (e.g., https://example.com:2). The depth tells the crawler how far to dig into the site’s link structure.
	•	Example: Typing https://example.com:2 tells PagesXcrawler to go two levels deep on example.com.
	•	The crawler will start from the homepage and go deeper into linked pages, gathering as much data as you specify.
	3.	Sit Back and Let PagesXcrawler Do Its Thing: The crawler will run automatically, saving everything it finds. All you have to do is wait about 60 seconds, then check the deployments page to see if your crawl is complete.

What You Get:

Once the crawl is complete, you’ll find:

	•	results.json: A JSON file with the latest crawl’s findings, perfect for processing.
	•	results.csv: The same data in a CSV format, ideal for viewing in a spreadsheet.
	•	issue_status.csv: A log of all past crawls and their statuses.

This setup makes it easy to track what you’ve crawled and see the latest results without having to manage data manually. Everything is saved automatically, and the latest crawl always overwrites the previous results, so you’re not dealing with huge files of outdated data. But, if you’re interested in tracking your progress, issue_status.csv keeps a record of all past runs.

Key Things to Remember:

	•	Single-User Mode: PagesXcrawler is designed to serve one person at a time. If multiple people want to use it, they can fork the repo and add their own Actions key. Just add it to the environment variables, and you’re good to go!
	•	Depth and Crawl Time: The deeper the crawl, the longer it will take. Certain sites may take longer, especially those with complex URLs or special characters like slashes. At the moment, those URLs might be tricky, but future updates are planned to fix this.
	•	Checking the Status: Since there’s no real-time status indicator, you may need to give it a minute before checking the deployments page to see the latest crawl status.

Why Use PagesXcrawler?

PagesXcrawler is perfect for anyone who wants to quickly gather data from a website, whether for SEO analysis, research, or simply exploring a website’s structure. Think of it as a handy tool that lets you explore a site’s full structure with zero effort. With PagesXcrawler, you’re one issue post away from gathering every link on a site, and it’s all automated—no extra steps, no learning curve.

Try it out, explore a site, and let me know what you think. Happy crawling!
