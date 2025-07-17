#!/usr/bin/env bash
# build.sh
echo "Starting build process..."

# Install system dependencies for OpenCV (if apt-get is available)
if command -v apt-get &> /dev/null; then
    echo "Installing system dependencies for OpenCV..."
    apt-get update
    apt-get install -y \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        libgomp1 \
        libglu1-mesa \
        libgl1-mesa-glx \
        libglib2.0-0 \
        libsm6 \
        libxrender1 \
        libxext6 \
        libgl1-mesa-dev \
        python3-opencv \
        ffmpeg \
        libsm6 \
        libxext6
else
    echo "apt-get not available, skipping system dependencies"
fi

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python requirements..."
pip install -r requirements.txt

# Install Playwright and its browser with proper path handling
echo "=== Installing Playwright and browsers ==="

# IMPORTANT: Use the default Playwright path instead of custom one
# This ensures consistency between build and runtime
echo "Installing Playwright with default paths..."

# First, unset any custom paths to use defaults
unset PLAYWRIGHT_BROWSERS_PATH

# Install Playwright browsers using default location
echo "Installing Chromium browser..."
playwright install chromium

# Install dependencies
echo "Installing Playwright system dependencies..."
playwright install-deps chromium || echo "System dependencies installation skipped"

# Verify the installation using default paths
echo "=== Verifying Playwright installation ==="
echo "Testing Playwright with default configuration..."
python -c "
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
    import traceback
    traceback.print_exc()
"

# Test if CV modules loaded
echo "=== Testing Python modules ==="
echo "Testing OpenCV installation..."
python -c "import cv2; print('✓ OpenCV version:', cv2.__version__)" || echo "✗ OpenCV not loaded"
echo "Testing scipy installation..."
python -c "import scipy; print('✓ scipy version:', scipy.__version__)" || echo "✗ scipy not loaded"
echo "Testing scikit-image installation..."
python -c "import skimage; print('✓ scikit-image version:', skimage.__version__)" || echo "✗ scikit-image not loaded"

echo "Build process completed!"

# Check static files after build
echo "=== Checking static files ==="
echo "Listing static/js directory:"
ls -la static/js/ | head -10
echo "Checking unified-analysis.js size:"
wc -c static/js/unified-analysis.js 2>/dev/null || echo "unified-analysis.js not found"

# Final summary
echo "=== Build Summary ==="
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"
echo "Current directory: $(pwd)"
echo "Playwright browsers location: $(python -c 'from playwright._impl._driver import get_driver_env; print(get_driver_env()["PLAYWRIGHT_BROWSERS_PATH"])' 2>/dev/null || echo 'default')"
echo "=== End Build Summary ==="
