# 🅿🅰🅶🅴🆂🆇🅲🆁🅰🆆🅻🅴🆁

[Previous sections remain the same until Parameters Reference Chart...]

### Parameters Reference Chart

| Parameter | Required | Default | Description | Example |
|-----------|:--------:|:-------:|-------------|----------|
| **url** | ✅ | - | The URL to crawl (any domain) | `https://example.com` |
| **depth** | ✅ | - | Number of link levels to follow | `3` |
| **max-pages** | ❌ | 100 | Maximum number of pages to crawl | `50` |
| **timeout** | ❌ | 10 | Request timeout in seconds | `15` |
| **requests-per-second** | ❌ | 2 | Rate limiting to avoid being blocked | `1.5` |
| **rotate-agent-after** | ❌ | 10 | Number of requests before rotating user agent | `5` |

### Example Issue Formats

```bash
# Basic format
https://example.com:depth(2)

# With single parameter
https://wikipedia.org:depth(1):params(max-pages=20)

# With multiple parameters including user agent rotation
https://github.com:depth(3):params(max-pages=50,timeout=15,requests-per-second=1,rotate-agent-after=5)
```

### User Agent Rotation

PagesXcrawler now includes intelligent user agent rotation to help avoid detection:

- Supports 20+ different user agents across multiple platforms
- Configurable rotation frequency
- Covers major browsers and operating systems
- Includes mobile user agents
- Automatic logging of rotations

Example with frequent rotation:
```bash
https://example.com:depth(2):params(rotate-agent-after=5)
```

[Rest of the README remains the same...]

## Important Considerations

### Performance and Limitations

- **Crawling Depth**: Deeper depths may require longer processing times. Consider using the `max-pages` parameter for large sites.
- **Rate Limiting**: The crawler respects website load by limiting requests per second. Adjust with the `requests-per-second` parameter if needed.
- **User Agent Rotation**: More frequent rotation (`rotate-agent-after`) may help avoid detection but could affect performance.
- **Timeout Settings**: Default timeout is 10 seconds per request. For slow sites, increase with the `timeout` parameter.
- **Resource Usage**: A typical crawl with depth 3 and 100 pages takes approximately 2-3 minutes to complete.

[Rest of the README continues...]

## Recent Enhancements

- **User Agent Rotation**: Configurable rotation of user agents to avoid detection
- **Enhanced Metadata Extraction**: Now captures favicon, canonical URL, social media tags, and more
- **Improved UI**: Modern, responsive dashboard with better styling and usability
- **Advanced Filtering**: Filter by domain, content type, and depth
- **Clickable Cards**: Navigate directly to crawled pages from the dashboard
- **Issue Comments**: Real-time progress updates during crawling
- **Parameter Support**: Additional crawling parameters for fine-tuned control
- **Better Error Handling**: More robust error recovery and reporting

[Continue with existing content...]
