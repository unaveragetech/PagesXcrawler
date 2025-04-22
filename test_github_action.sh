#!/bin/bash
# Test script to simulate the GitHub Actions workflow

# Set test issue title and number
issue_title="crawl: https://example.com 2 --max-pages 20 --timeout 10 --rotate-agent-after 5"
issue_number="149"

echo "Testing with issue title: $issue_title"

# Match the new format: crawl: URL DEPTH [OPTIONS]
if [[ "$issue_title" =~ ^crawl:[[:space:]]*(https?://[^[:space:]]+)[[:space:]]+([0-9]+)(.*)$ ]]; then
    url="${BASH_REMATCH[1]}"
    depth="${BASH_REMATCH[2]}"
    options="${BASH_REMATCH[3]}"
    
    # Set default values
    max_pages=100
    timeout=10
    rotate_agent=10
    
    # Parse options if they exist
    if [ ! -z "$options" ]; then
        # Check for --max-pages
        if [[ "$options" =~ --max-pages[[:space:]]+([0-9]+) ]]; then
            max_pages="${BASH_REMATCH[1]}"
        fi
        
        # Check for --timeout
        if [[ "$options" =~ --timeout[[:space:]]+([0-9]+) ]]; then
            timeout="${BASH_REMATCH[1]}"
        fi
        
        # Check for --rotate-agent-after
        if [[ "$options" =~ --rotate-agent-after[[:space:]]+([0-9]+) ]]; then
            rotate_agent="${BASH_REMATCH[1]}"
        fi
    fi
    
    echo "Parsed values:"
    echo "URL: $url"
    echo "DEPTH: $depth"
    echo "MAX_PAGES: $max_pages"
    echo "TIMEOUT: $timeout"
    echo "ROTATE_AGENT: $rotate_agent"
    
    echo "Running crawler command:"
    echo "python crawler.py \"$url\" \"$depth\" --max-pages \"$max_pages\" --timeout \"$timeout\" --rotate-agent-after \"$rotate_agent\""
else
    echo "Error: Issue title must be in the format 'crawl: URL DEPTH [OPTIONS]'"
    exit 1
fi
