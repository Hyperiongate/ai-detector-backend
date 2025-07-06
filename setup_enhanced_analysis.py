#!/usr/bin/env python3
"""
Setup script to download required NLTK data and spaCy models
Run this after installing requirements.txt
"""

import nltk
import subprocess
import sys

def setup_nltk_data():
    """Download required NLTK data packages"""
    print("Downloading NLTK data packages...")
    
    nltk_packages = [
        'punkt',
        'stopwords',
        'vader_lexicon',
        'averaged_perceptron_tagger',
        'maxent_ne_chunker',
        'words'
    ]
    
    for package in nltk_packages:
        try:
            nltk.download(package, quiet=True)
            print(f"✓ Downloaded {package}")
        except Exception as e:
            print(f"✗ Failed to download {package}: {e}")

def setup_spacy_models():
    """Download required spaCy models"""
    print("\nDownloading spaCy models...")
    
    try:
        # Download the small English model
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        print("✓ Downloaded en_core_web_sm")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to download spaCy model: {e}")
        print("You can manually download it with: python -m spacy download en_core_web_sm")

def verify_installation():
    """Verify that all components are properly installed"""
    print("\nVerifying installation...")
    
    # Test imports
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("✓ spaCy model loaded successfully")
    except:
        print("✗ spaCy model not found")
    
    try:
        from nltk.sentiment import SentimentIntensityAnalyzer
        sia = SentimentIntensityAnalyzer()
        print("✓ NLTK sentiment analyzer ready")
    except:
        print("✗ NLTK sentiment analyzer not ready")
    
    try:
        from transformers import pipeline
        print("✓ Transformers library ready")
    except:
        print("✗ Transformers library not ready")

if __name__ == "__main__":
    print("Setting up Enhanced Content Analysis dependencies...\n")
    
    setup_nltk_data()
    setup_spacy_models()
    verify_installation()
    
    print("\nSetup complete! The enhanced content analysis module is ready to use.")
