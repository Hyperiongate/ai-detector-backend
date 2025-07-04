#!/usr/bin/env bash
# build.sh

# Update package lists
apt-get update

# Install system dependencies for OpenCV
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
    libgl1-mesa-dev

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Test if CV modules loaded
python -c "import cv2; print('OpenCV version:', cv2.__version__)"
