# PagesXcrawler Technical Documentation

[Previous sections remain the same until User Agent Management...]

## 2. Crawler Engine

### 2.1 User Agent Management

The crawler implements a sophisticated user agent rotation system:

#### Available User Agents

| Category | Browser | Version | Example |
|----------|---------|---------|---------|
| **Windows** | Chrome | 91.0 | `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ...` |
| | | 92.0 | `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ...` |
| | | 93.0 | `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ...` |
| | Firefox | 90.0 | `Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) ...` |
| | | 91.0 | `Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) ...` |
| | | 92.0 | `Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) ...` |
| | Edge | 91.0 | `Mozilla/5.0 (Windows NT 10.0; Win64; x64) ... Edg/91.0` |
| | | 92.0 | `Mozilla/5.0 (Windows NT 10.0; Win64; x64) ... Edg/92.0` |
| **macOS** | Safari | 14.1.2 | `Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ...` |
| | Chrome | 91.0 | `Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ...` |
| | | 92.0 | `Mozilla/5.0 (Macintosh; Intel Mac OS X 11_5_2) ...` |
| | Firefox | 90.0 | `Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:90.0) ...` |
| | | 91.0 | `Mozilla/5.0 (Macintosh; Intel Mac OS X 11.5; rv:91.0) ...` |
| **Linux** | Chrome | 91.0 | `Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 ...` |
| | | 92.0 | `Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 ...` |
| | Firefox | 90.0 | `Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) ...` |
| | | 91.0 | `Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) ...` |
| **Mobile** | Android | Chrome | `Mozilla/5.0 (Linux; Android 11; SM-G991B) ...` |
| | iOS | Safari | `Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) ...` |

#### User Agent Rotation

The crawler now supports configurable user agent rotation:

```python
class RateLimiter:
    def __init__(self, initial_requests_per_second=2, rotate_agent_after=10):
        self.rotate_after = rotate_agent_after
        self.requests_since_rotation = 0
```

#### Command-Line Arguments

| Argument | Description | Default | Example |
|-----------|-------------|---------|---------|
| `--rotate-agent-after` | Number of requests before rotating user agent | 10 | `--rotate-agent-after 5` |

Example usage with user agent rotation:
```bash
python crawler.py "https://example.com" 2 --rotate-agent-after 5
```

This will rotate the user agent after every 5 requests, helping to avoid detection while crawling.

#### Rotation Strategy

1. User agents are randomly shuffled on initialization
2. System rotates through agents after specified number of requests
3. Rotation is logged for monitoring
4. Counter resets after each rotation
5. Rotation occurs across all categories for maximum variety

### 2.2 Smart Rate Limiting

[Rest of the documentation remains the same...]

## 3. Command-Line Arguments Reference

Updated command-line arguments table:

| Argument | Required | Default | Description | Example |
|-----------|:--------:|:-------:|-------------|---------|
| **url** | ✅ | - | The URL to crawl | `https://example.com` |
| **depth** | ✅ | - | Number of link levels to follow | `3` |
| **--max-pages** | ❌ | 100 | Maximum number of pages to crawl | `--max-pages 50` |
| **--timeout** | ❌ | 10 | Request timeout in seconds | `--timeout 15` |
| **requests-per-second** | ❌ | 2 | Initial rate limiting (handled automatically) | N/A |
| **--rotate-agent-after** | ❌ | 10 | Requests before agent rotation | `--rotate-agent-after 5` |

[Rest of the documentation continues...]

### Advanced Usage Examples

```bash
# Basic crawl with default rotation
python crawler.py "https://example.com" 2

# Fast crawl with frequent rotation
python crawler.py "https://example.com" 2 --rotate-agent-after 5

# Careful crawl with slow rotation
python crawler.py "https://example.com" 2 --rotate-agent-after 20 --timeout 20
```

[Continue with existing documentation...]
