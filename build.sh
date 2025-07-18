#!/usr/bin/env bash
# Exit on error
set -e

# Set the Playwright browsers path to a persistent location
export PLAYWRIGHT_BROWSERS_PATH="/opt/render/project/.playwright-browsers"

echo "=== Checking Playwright's browser path ==="
echo "Playwright expects browsers at: $PLAYWRIGHT_BROWSERS_PATH"

# Install Python dependencies
pip install -r requirements.txt

# Ensure playwright is installed
pip install playwright

# Install browsers to the persistent location
echo "=== Installing Playwright browsers ==="
playwright install chromium

echo "=== Finding installed browsers ==="
find $PLAYWRIGHT_BROWSERS_PATH -name "chrome" -type f 2>/dev/null || echo "No Chrome found yet"

# Test playwright
echo "=== Testing Playwright ==="
python -c "
from playwright.sync_api import sync_playwright
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        browser.close()
        print('✓ Playwright test successful')
except Exception as e:
    print(f'✗ Playwright test failed: {e}')
"

echo "Build process completed!"
