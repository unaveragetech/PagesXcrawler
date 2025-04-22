# PowerShell script to test the regex pattern

$issue_title = "crawl: https://example.com 2 --max-pages 20 --timeout 10 --rotate-agent-after 5"
$issue_number = "149"

# Use PowerShell regex to match the new format
if ($issue_title -match '^crawl:\s*(https?://[^\s]+)\s+(\d+)(.*)$') {
    $url = $matches[1]
    $depth = $matches[2]
    $options = $matches[3]
    
    # Set default values
    $max_pages = 100
    $timeout = 10
    $rotate_agent = 10
    
    # Parse options if they exist
    if ($options) {
        # Check for --max-pages
        if ($options -match '--max-pages\s+(\d+)') {
            $max_pages = $matches[1]
        }
        
        # Check for --timeout
        if ($options -match '--timeout\s+(\d+)') {
            $timeout = $matches[1]
        }
        
        # Check for --rotate-agent-after
        if ($options -match '--rotate-agent-after\s+(\d+)') {
            $rotate_agent = $matches[1]
        }
    }
    
    Write-Host "URL: $url"
    Write-Host "DEPTH: $depth"
    Write-Host "MAX_PAGES: $max_pages"
    Write-Host "TIMEOUT: $timeout"
    Write-Host "ROTATE_AGENT: $rotate_agent"
    Write-Host "ISSUE_TITLE: $issue_title"
    Write-Host "ISSUE_NUMBER: $issue_number"
}
else {
    Write-Host "Error: Issue title must be in the format 'crawl: URL DEPTH [OPTIONS]'"
    exit 1
}
