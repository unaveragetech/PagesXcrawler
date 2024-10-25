# Web Crawler System
This repository contains a web crawler that runs automatically using GitHub Actions.
When a user creates an issue with the format `url:depth`, the crawler fetches links
from the specified URL up to the specified depth. The results are stored in JSON and
CSV formats and displayed on a GitHub Pages site.

## Usage
To use the system, create a new issue in the format:
```
https://example.com:2
```
