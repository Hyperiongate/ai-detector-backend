#!/usr/bin/env bash
# build.sh
echo "Starting build process..."

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python requirements..."
pip install -r requirements.txt

# Install Playwright browsers with the correct environment variable
echo "=== Installing Playwright and browsers ==="

# Set the browsers path BEFORE installation
export PLAYWRIGHT_BROWSERS_PATH="/opt/render/.cache/ms-playwright"
mkdir -p $PLAYWRIGHT_BROWSERS_PATH

# Install playwright
pip install playwright

# Install chromium with the path already set
python -m playwright install chromium

# Install system dependencies if needed
python -m playwright install-deps chromium || echo "System dependencies installation skipped"

# Verify installation
echo "=== Verifying Playwright installation ==="
python -c "
import os
os.environ['PLAYWRIGHT_BROWSERS_PATH'] = '/opt/render/.cache/ms-playwright'
try:
    from playwright.sync_api import sync_playwright
    print('✓ Playwright imported successfully')
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = browser.new_page()
        page.goto('about:blank')
        browser.close()
        print('✓ Playwright browser test successful')
except Exception as e:
    print(f'✗ Playwright test failed: {e}')
"

echo "Build process completed!"
