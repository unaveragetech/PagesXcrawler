



  🅿🅰🅶🅴🆂🆇🅲🆁🅰🆆🅻🅴🆁 
٩ʕ◕౪◕ʔو.url  ٩ʕ◕౪◕ʔو hmm.

- Web Crawler System -


![Deployments](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/unaveragetech/PagesXcrawler/main/data/deployments.json)
![Actions](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/unaveragetech/PagesXcrawler/main/data/actions.json)
![Successful Actions](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/unaveragetech/PagesXcrawler/main/data/successful_actions.json)
![Failed Actions](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/unaveragetech/PagesXcrawler/main/data/failed_actions.json)

<details>
  <summary>Actions and Deployments Chart</summary>
  
  ![Actions and Deployments Chart](https://raw.githubusercontent.com/unaveragetech/PagesXcrawler/main/data/actions_chart.png)
</details>

Welcome to the PagesXcrawler repository! This documentation outlines how to use our automated web crawler, powered by GitHub Actions, which retrieves links from specified websites based on user-defined depth and displays the results on a GitHub Pages site.

## Quick Links

<div style="display: flex; flex-direction: column; gap: 10px;">

  <a href="Documentation.md" style="text-decoration: none; color: white; background-color: #007acc; padding: 10px 15px; border: 1px solid #005fa3; border-radius: 5px; text-align: center; font-weight: bold;">Documentation</a>

  <a href="https://theuselessweb.com" style="text-decoration: none; color: white; background-color: #007acc; padding: 10px 15px; border: 1px solid #005fa3; border-radius: 5px; text-align: center; font-weight: bold;">Find a Site to Crawl</a>

  <a href="https://github.com/unaveragetech/PagesXcrawler/issues/new" style="text-decoration: none; color: white; background-color: #007acc; padding: 10px 15px; border: 1px solid #005fa3; border-radius: 5px; text-align: center; font-weight: bold;">Create a Crawl Issue</a>

  <a href="https://github.com/unaveragetech/PagesXcrawler/deployments" style="text-decoration: none; color: white; background-color: #007acc; padding: 10px 15px; border: 1px solid #005fa3; border-radius: 5px; text-align: center; font-weight: bold;">Check Deployment Jobs</a>

  <a href="https://github.com/unaveragetech/PagesXcrawler/blob/main/data/results.csv" style="text-decoration: none; color: white; background-color: #007acc; padding: 10px 15px; border: 1px solid #005fa3; border-radius: 5px; text-align: center; font-weight: bold;">View Last Run Results</a>

  <a href="https://github.com/unaveragetech/PagesXcrawler/blob/main/data/issues_status.csv" style="text-decoration: none; color: white; background-color: #007acc; padding: 10px 15px; border: 1px solid #005fa3; border-radius: 5px; text-align: center; font-weight: bold;">Access All Run History</a>

  <a href="https://unaveragetech.github.io/PagesXcrawler/" style="text-decoration: none; color: white; background-color: #007acc; padding: 10px 15px; border: 1px solid #005fa3; border-radius: 5px; text-align: center; font-weight: bold;">View Results Chart</a>

</div>


## How It Works

### 1. Issue Creation

To start a crawl, create a new issue using the following format:

```
url:depth(int)
```

For example:

```
https://puginarug.com:depth(3)
```

- **url**: The URL of the webpage you wish to crawl.
- **depth**: The number of link levels to follow from the initial URL. In the example above, a depth of `3` means the crawler will retrieve links from the starting page and from pages linked up to three levels deep.

### 2. Crawling Process

After submitting your issue, the crawler is automatically triggered:

- It fetches links based on your specified depth.
- The results are saved in both JSON and CSV formats within the `data` directory.

### 3. Results Storage

- **CSV Format**: Easily viewable on GitHub and compatible with spreadsheet applications.
- **JSON Format**: Used to dynamically load results into the HTML page at the [Main Chart](https://unaveragetech.github.io/PagesXcrawler/).

### 4. Reloading the Page
navigate here to view link cards 
 **[View Cards](https://unaveragetech.github.io/PagesXcrawler/)**
If the page does not display the latest results after deployment, simply refresh the page.

### 5. Overwriting Previous Fetches

To replace the results of your last crawl, submit a new issue with the same format. The system will update the previous data with the latest crawl results.

## Important Considerations

- **Submission Format**: Adhere to the correct issue submission format (`url:depth(int)`) for proper functionality.
- **Crawling Depth**: Deeper depths may require longer processing times, as the crawler fetches more data. However, it operates in a powerful environment, ensuring responsiveness.
```
Using the URL https://github.com/unaveragetech and a specified depth of 3, the web crawler performed its operations, which included crawling the website and executing the necessary deployment processes. The total time taken for this task was approximately 2 minutes.

Out of this total duration, the crawling process itself took around 1 minute and 27 seconds. The remaining time was utilized for deployment checks, ensuring that all relevant data was accurately processed and deployed. This breakdown highlights the efficiency of the crawler while also emphasizing the importance of thorough checks in the deployment phase.
```
## Setting Up for Private Use

If you want to use this system privately after forking the repository, follow these steps:

### 1. Fork the Repository

Click the "Fork" button in the upper right corner of the GitHub repository page.

### 2. Clone Your Fork

Clone your forked repository to your local machine:

```bash
git clone https://github.com/yourusername/PagesXcrawler.git
```

### 3. Configure GitHub Actions

Enable GitHub Actions in your private repository:

- Go to the "Settings" tab.
- Under "Actions," select "General."
- Make sure actions are enabled.

### 4. Set Up Secrets

For proper functionality, set up any required secrets (like Personal Access Tokens):

- Navigate to "Settings" > "Secrets and variables" > "Actions."
- Click "New repository secret" and add your secrets (name it `MY_PAT`), ensuring it has the necessary read and write scopes.

### 5. Update the `_config.yml`

Ensure the `_config.yml` file is configured to your repository settings and URLs. Although this file helps mitigate Jekyll issues, it can be left empty if not needed.

### 6. Test the System

Create a test issue in the format `url:depth` to verify that everything works correctly. If successful, you’ll see the bot’s actions, and the issue will close. If there’s an error (like 128, 104, or 404), it typically indicates permission issues with the token.

## Additional Features

- **Automation**: Automates data retrieval, allowing users to focus on analysis instead of manual fetching.
- **Customization**: Developers can adjust the crawler’s behavior and settings based on specific needs.

## Conclusion

The PagesXcrawler system offers an efficient solution for retrieving and visualizing web data with ease. If you have any questions, suggestions, or issues, don’t hesitate to create a new issue in the repository!
