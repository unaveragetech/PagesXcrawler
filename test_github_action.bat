@echo off
echo Testing GitHub Actions workflow locally

REM Run the PowerShell script
powershell -ExecutionPolicy Bypass -File test_regex.ps1

echo.
echo If the above output shows the correct parsed values, the regex pattern is working correctly.
echo.
echo To test the crawler with these values, run:
echo python crawler.py "https://example.com" 2 --max-pages 20 --timeout 10 --rotate-agent-after 5
