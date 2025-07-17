"""
Playwright configuration to ensure consistent browser paths
"""
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check if we're running on Render
is_render = os.environ.get('RENDER') == 'true'

if is_render:
    # On Render, we MUST set the browser path
    browser_path = '/opt/render/.cache/ms-playwright'
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = browser_path
    logger.info(f"Running on Render - PLAYWRIGHT_BROWSERS_PATH set to: {browser_path}")
    
    # Verify the path exists
    if os.path.exists(browser_path):
        logger.info(f"✓ Browser path exists: {browser_path}")
        # Check for chromium specifically
        chromium_path = os.path.join(browser_path, 'chromium-1091')
        if os.path.exists(chromium_path):
            logger.info(f"✓ Chromium found at: {chromium_path}")
        else:
            logger.warning(f"✗ Chromium NOT found at: {chromium_path}")
    else:
        logger.warning(f"✗ Browser path does NOT exist: {browser_path}")
else:
    # For local development
    if 'PLAYWRIGHT_BROWSERS_PATH' in os.environ:
        logger.info(f"Local environment - Current PLAYWRIGHT_BROWSERS_PATH: {os.environ['PLAYWRIGHT_BROWSERS_PATH']}")
    else:
        logger.info("Local environment - No PLAYWRIGHT_BROWSERS_PATH set, using defaults")

logger.info("Playwright config loaded successfully")
