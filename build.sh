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

# Set the Playwright browsers path explicitly
export PLAYWRIGHT_BROWSERS_PATH=/opt/render/.cache/ms-playwright
echo "PLAYWRIGHT_BROWSERS_PATH set to: $PLAYWRIGHT_BROWSERS_PATH"

# Create the directory if it doesn't exist
mkdir -p $PLAYWRIGHT_BROWSERS_PATH

# Install Playwright browsers with explicit path
echo "Installing Chromium browser..."
PLAYWRIGHT_BROWSERS_PATH=$PLAYWRIGHT_BROWSERS_PATH playwright install chromium

# Try to install system dependencies (this may fail on Render, but that's okay)
echo "Attempting to install Playwright system dependencies..."
PLAYWRIGHT_BROWSERS_PATH=$PLAYWRIGHT_BROWSERS_PATH playwright install-deps chromium || echo "System dependencies installation failed (this is expected on Render)"

# Verify the installation
echo "=== Verifying Playwright installation ==="
echo "Checking Playwright browsers directory..."
ls -la $PLAYWRIGHT_BROWSERS_PATH/ || echo "Playwright directory not found"

# Look for Chrome executable in common locations
echo "Looking for Chrome executable..."
find $PLAYWRIGHT_BROWSERS_PATH -name "chrome" -type f 2>/dev/null | head -5 || echo "Chrome executable not found with find"

# Check specific paths
for chromium_dir in $PLAYWRIGHT_BROWSERS_PATH/chromium-*/; do
    if [ -d "$chromium_dir" ]; then
        echo "Found Chromium directory: $chromium_dir"
        ls -la "$chromium_dir" | head -5
        if [ -f "$chromium_dir/chrome-linux/chrome" ]; then
            echo "✓ Chrome executable found at: $chromium_dir/chrome-linux/chrome"
        else
            echo "✗ Chrome executable not found in: $chromium_dir"
        fi
    fi
done

# Test if CV modules loaded
echo "=== Testing Python modules ==="
echo "Testing OpenCV installation..."
python -c "import cv2; print('✓ OpenCV version:', cv2.__version__)" || echo "✗ OpenCV not loaded"
echo "Testing scipy installation..."
python -c "import scipy; print('✓ scipy version:', scipy.__version__)" || echo "✗ scipy not loaded"
echo "Testing scikit-image installation..."
python -c "import skimage; print('✓ scikit-image version:', skimage.__version__)" || echo "✗ scikit-image not loaded"

# Test Playwright installation with path
echo "Testing Playwright installation..."
PLAYWRIGHT_BROWSERS_PATH=$PLAYWRIGHT_BROWSERS_PATH python -c "
import os
os.environ['PLAYWRIGHT_BROWSERS_PATH'] = '/opt/render/.cache/ms-playwright'
try:
    from playwright.sync_api import sync_playwright
    print('✓ Playwright imported successfully')
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
        browser.close()
        print('✓ Playwright browser test successful')
except Exception as e:
    print(f'✗ Playwright test failed: {e}')
"

echo "Build process completed!"

# Check static files after build
echo "=== Checking static files ==="
echo "Listing static/js directory:"
ls -la static/js/ | head -10
echo "Checking unified-analysis.js size:"
wc -c static/js/unified-analysis.js
echo "First 100 chars of unified-analysis.js:"
head -c 100 static/js/unified-analysis.js
echo ""
echo "=== End static file check ==="

# Final summary
echo "=== Build Summary ==="
echo "PLAYWRIGHT_BROWSERS_PATH: $PLAYWRIGHT_BROWSERS_PATH"
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"
echo "Current directory: $(pwd)"
echo "=== End Build Summary ==="
