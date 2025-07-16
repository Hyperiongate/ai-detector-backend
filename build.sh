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

# Install Playwright and its browser
echo "Installing Playwright browsers..."
playwright install chromium
echo "Installing Playwright system dependencies..."
playwright install-deps chromium

# Test if CV modules loaded
echo "Testing OpenCV installation..."
python -c "import cv2; print('✓ OpenCV version:', cv2.__version__)" || echo "✗ OpenCV not loaded"
echo "Testing scipy installation..."
python -c "import scipy; print('✓ scipy version:', scipy.__version__)" || echo "✗ scipy not loaded"
echo "Testing scikit-image installation..."
python -c "import skimage; print('✓ scikit-image version:', skimage.__version__)" || echo "✗ scikit-image not loaded"

# Test Playwright installation
echo "Testing Playwright installation..."
python -c "import playwright; print('✓ Playwright installed successfully')" || echo "✗ Playwright not loaded"

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
