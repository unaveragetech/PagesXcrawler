# Test script to simulate the GitHub Actions workflow locally

# Define test parameters
$url = "https://example.com"
$depth = 2
$max_pages = 20
$timeout = 10
$rotate_agent = 5

Write-Host "Running crawler with configuration:"
Write-Host "URL: $url"
Write-Host "Depth: $depth"
Write-Host "Max Pages: $max_pages"
Write-Host "Timeout: $timeout"
Write-Host "Rotate Agent: $rotate_agent"

# Run the crawler
python crawler.py "$url" $depth --max-pages $max_pages --timeout $timeout --rotate-agent-after $rotate_agent

# Update visualization
python scripts/update_html.py

Write-Host "Test completed! Check the data directory for results."
