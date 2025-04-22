# 🅿🅰🅶🅴🆂🆇🅲🆁🅰🆆🅻🅴🆁
٩ʕ◕౪◕ʔو.url  ٩ʕ◕౪◕ʔو hmm.

[Previous sections remain the same until Usage Methods...]

## Usage Methods

PagesXcrawler offers two ways to use the system:

### 1. GitHub Issues Method
Create a new issue using one of these formats:

**Basic format:**
```
url:depth(n)
```

**Advanced format with parameters:**
```
url:depth(n):params(param1=value1,param2=value2)
```

Examples:
```
https://example.com:depth(3)
https://example.com:depth(2):params(max-pages=50,timeout=15)
https://github.com:depth(3):params(max-pages=50,timeout=15,rotate-agent-after=5)
```

> ⚠️ **Important**: When using GitHub Issues, the format must be exact. Don't include command-line style arguments.

### 2. Command-Line Method
Run directly from the command line:
```bash
python crawler.py URL DEPTH [OPTIONS]
```

Examples:
```bash
# Basic crawl
python crawler.py "https://example.com" 2

# With parameters
python crawler.py "https://example.com" 2 --max-pages 50 --timeout 15 --rotate-agent-after 5
```

## Format Reference

### GitHub Issues Format
✅ Correct:
```
https://example.com:depth(3)
https://example.com:depth(2):params(max-pages=50)
```

❌ Incorrect:
```
https://example.com 3 --max-pages 50
https://example.com:depth(3) --timeout 15
```

### Command Line Format
✅ Correct:
```bash
python crawler.py "https://example.com" 3
python crawler.py "https://example.com" 2 --max-pages 50
```

❌ Incorrect:
```bash
python crawler.py "https://example.com:depth(3)"
python crawler.py https://example.com:depth(2):params(max-pages=50)
```

[Rest of the README remains the same...]
