"""
Computer Vision utilities - Safe imports and initialization
"""
import time
import numpy as np

# Computer Vision imports for enhanced image analysis
CV_AVAILABLE = False
cv2 = None
scipy = None
skimage = None
stats = None
feature = None
filters = None
morphology = None
exposure = None
structural_similarity = None
fftpack = None
exifread = None

# Add delay and retry logic for module loading
for attempt in range(3):
    try:
        # Import numpy first if not already imported
        import numpy as np
        
        # Try importing CV modules with explicit error handling
        import cv2
        from scipy import fftpack
        import scipy.stats as stats
        from skimage import feature, filters, morphology, exposure
        from skimage.metrics import structural_similarity
        import exifread
        from collections import Counter
        
        # Verify opencv is actually working by running a simple operation
        test_array = np.zeros((10, 10), dtype=np.uint8)
        test_result = cv2.Laplacian(test_array, cv2.CV_64F)
        
        # Verify scipy works
        test_fft = fftpack.fft2(test_array)
        
        # Verify skimage works
        test_edges = feature.canny(test_array)
        
        CV_AVAILABLE = True
        print(f"✓ Computer vision modules loaded successfully (attempt {attempt + 1})")
        print(f"  - OpenCV version: {cv2.__version__}")
        print(f"  - All modules verified and working")
        break
        
    except ImportError as e:
        print(f"⚠ CV import error (attempt {attempt + 1}): {str(e)}")
        print(f"  - Missing module: {e.name if hasattr(e, 'name') else 'unknown'}")
        if attempt < 2:
            time.sleep(1.0)  # Wait 1 second before retry
            
    except Exception as e:
        print(f"⚠ CV runtime error (attempt {attempt + 1}): {type(e).__name__}: {str(e)}")
        if attempt < 2:
            time.sleep(1.0)
            
if not CV_AVAILABLE:
    print("⚠ Computer vision modules not available after 3 attempts - will use basic image analysis")
    print("  - This may be due to missing system dependencies or incomplete installation")
    
    # Set module variables to None for safety
    cv2 = None
    scipy = None
    feature = None
    filters = None
    morphology = None
    exposure = None
    structural_similarity = None
    fftpack = None
    stats = None
    exifread = None
