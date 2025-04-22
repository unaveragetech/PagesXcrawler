# 🅿🅰🅶🅴🆂🆇🅲🆁🅰🆆🅻🅴🆁

[Previous sections remain the same until Parameters Reference Chart...]

### Command-Line Arguments Reference

| Argument | Required | Default | Description | Example |
|-----------|:--------:|:-------:|-------------|----------|
| **url** | ✅ | - | The URL to crawl (any domain) | `https://example.com` |
| **depth** | ✅ | - | Number of link levels to follow | `3` |
| **--max-pages** | ❌ | 100 | Maximum number of pages to crawl | `--max-pages 50` |
| **--timeout** | ❌ | 10 | Request timeout in seconds | `--timeout 15` |
| **--rotate-agent-after** | ❌ | 10 | Number of requests before rotating user agent | `--rotate-agent-after 5` |

### Example Command Formats

```bash
# Basic format
python crawler.py "https://example.com" 2

# With single parameter
python crawler.py "https://wikipedia.org" 1 --max-pages 20

# With multiple parameters including user agent rotation
python crawler.py "https://github.com" 3 --max-pages 50 --timeout 15 --rotate-agent-after 5
```

> **Note**: Always enclose the URL in quotes to prevent issues with special characters, especially in PowerShell.

### User Agent Rotation

PagesXcrawler now includes intelligent user agent rotation to help avoid detection:

- Supports 20+ different user agents across multiple platforms
- Configurable rotation frequency
- Covers major browsers and operating systems
- Includes mobile user agents
- Automatic logging of rotations

Example with frequent rotation:
```bash
python crawler.py "https://example.com" 2 --rotate-agent-after 5
```

## Command-Line Usage

PagesXcrawler can be run directly from the command line using the following syntax:

```bash
python crawler.py URL DEPTH [OPTIONS]
```

Where:
- `URL` is the starting URL to crawl (required)
- `DEPTH` is the number of link levels to follow (required)
- `OPTIONS` are additional optional arguments

### Available Options

```
--max-pages MAX_PAGES     Maximum number of pages to crawl (default: 100)
--timeout TIMEOUT         Request timeout in seconds (default: 10)
--rotate-agent-after N    Number of requests after which to rotate user agent (default: 10)
```

### Command-Line Examples

```bash
# Basic crawl of example.com with depth 2
python crawler.py "https://example.com" 2

# Crawl with a 20-second timeout
python crawler.py "https://example.com" 2 --timeout 20

# Limit to 30 pages and rotate user agent frequently
python crawler.py "https://example.com" 3 --max-pages 30 --rotate-agent-after 3

# Full example with all options
python crawler.py "https://github.com" 3 --max-pages 50 --timeout 15 --rotate-agent-after 5
```

> **Important**: When using PowerShell, always enclose the URL in quotes to prevent parsing errors with special characters.

## Important Considerations

### Performance and Limitations

- **Crawling Depth**: Deeper depths may require longer processing times. Consider using the `--max-pages` parameter for large sites.
- **Rate Limiting**: The crawler respects website load by limiting requests per second. The rate limiting is handled automatically by the crawler.
- **User Agent Rotation**: More frequent rotation (`--rotate-agent-after`) may help avoid detection but could affect performance.
- **Timeout Settings**: Default timeout is 10 seconds per request. For slow sites, increase with the `--timeout` parameter.
- **Resource Usage**: A typical crawl with depth 3 and 100 pages takes approximately 2-3 minutes to complete.

[Rest of the README continues...]

## Recent Enhancements

- **User Agent Rotation**: Configurable rotation of user agents to avoid detection
- **Enhanced Metadata Extraction**: Now captures favicon, canonical URL, social media tags, and more
- **Improved UI**: Modern, responsive dashboard with better styling and usability
- **Advanced Filtering**: Filter by domain, content type, and depth
- **Clickable Cards**: Navigate directly to crawled pages from the dashboard
- **Issue Comments**: Real-time progress updates during crawling
- **Command-Line Arguments**: Additional command-line arguments for fine-tuned control
- **Better Error Handling**: More robust error recovery and reporting

[Continue with existing content...]
