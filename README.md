
# Web Crawler System Hosted on GitHub Pages

This repository contains a fully automated web crawler powered by GitHub Actions. The crawler retrieves links from specified URLs based on user-defined depth and displays the results on a GitHub Pages site. 

## Find the Results Here

[View Results](https://unaveragetech.github.io/PagesXcrawler/)

## How It Works

### 1. Issue Creation

To initiate a crawl, users must create a new issue in the format:

```
https://example.com:2
```

- **URL**: The webpage you want to crawl.
- **Depth**: The number of levels the crawler should follow links from the initial URL. For example, a depth of `2` means it will retrieve links from the initial page and the pages linked from there.

### 2. Crawling Process

Once the issue is submitted, the system automatically triggers the web crawler:

- The crawler fetches links according to the specified depth.
- Results are stored in both JSON and CSV formats within the `data` directory.

### 3. Results Storage

- **CSV**: This format is easily viewable from GitHub and suitable for spreadsheet applications.
- **JSON**: This format is utilized to dynamically load results into the HTML page hosted at [https://unaveragetech.github.io/PagesXcrawler/](https://unaveragetech.github.io/PagesXcrawler/).

### 4. Reloading the Page

If the page does not load after deployment, simply refresh the page to see the latest results.

### 5. Overwriting Previous Fetches

Users can overwrite the results of the last crawl by posting a new issue. The system will replace the previous data with the latest crawl results.

## Important Considerations

- **Submission Order**: Ensure you follow the correct issue submission format (`url:depth`) for the crawler to function correctly.
  
- **Crawling Depth**: Keep in mind that deeper depths may lead to longer processing times, as the crawler retrieves more data.

## Setting Up for Private Use

If you wish to use this system privately after forking the repository, follow these key steps:

### 1. Fork the Repository

- Go to the repository on GitHub and click the "Fork" button in the upper right corner.

### 2. Clone Your Fork

- Clone your forked repository to your local machine:

```bash
git clone https://github.com/yourusername/PagesXcrawler.git
```

### 3. Configure GitHub Actions

To enable GitHub Actions in your private repository:

- Navigate to the "Settings" tab of your repository.
- Under the "Actions" section, select "General."
- Ensure that actions are enabled for your repository.

### 4. Set Up Secrets

For the crawler to function properly, you need to set up any required secrets (like Personal Access Tokens) in your repository:

- Go to "Settings" > "Secrets and variables" > "Actions."
- Click on "New repository secret" and add your secrets (e.g., `MY_PAT`).

### 5. Update the `_config.yml`

- Ensure the `_config.yml` file reflects your own repository settings and URLs as needed.

### 6. Test the System

- Create a test issue in the format `url:depth` to verify that everything is functioning as expected.

## Additional Features

- **Automation**: The system automates the data retrieval process, allowing users to focus on analysis rather than manual fetching.
  
- **Customization**: Developers can modify the crawler's behavior and settings according to specific requirements.

## Conclusion

This web crawler system provides a robust solution for retrieving and visualizing web data effortlessly. If you have any questions, suggestions, or issues, feel free to create a new issue in the repository!
