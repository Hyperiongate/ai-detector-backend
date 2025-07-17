#!/usr/bin/env bash
# build.sh
echo "Starting build process..."

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright
pip install playwright

# Let's see where Playwright wants to install browsers by default
echo "=== Checking Playwright's default browser path ==="
python -c "
from playwright._impl._driver import get_driver_env
env = get_driver_env()
print(f'Playwright expects browsers at: {env.get(\"PLAYWRIGHT_BROWSERS_PATH\", \"default location\")}')
"

# Install browsers wherever Playwright wants them
echo "=== Installing Playwright browsers ==="
python -m playwright install chromium

# Verify where browsers were actually installed
echo "=== Finding installed browsers ==="
find /opt/render -name "chrome" -path "*/chrome-linux/chrome" 2>/dev/null | while read chrome_path; do
    echo "Found Chrome at: $chrome_path"
done

# Test Playwright
echo "=== Testing Playwright ==="
python -c "
try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        browser.close()
        print('✓ Playwright test successful')
except Exception as e:
    print(f'✗ Playwright test failed: {e}')
    import traceback
    traceback.print_exc()
"

echo "Build process completed!"
