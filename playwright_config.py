"""
Playwright configuration to ensure consistent browser paths
"""
import os
import logging

logger = logging.getLogger(__name__)

# Just log the current state - don't modify anything
browser_path = os.environ.get('PLAYWRIGHT_BROWSERS_PATH', 'Not set')
logger.info(f"Playwright config loaded - PLAYWRIGHT_BROWSERS_PATH: {browser_path}")

# More detailed debugging
if browser_path != 'Not set':
    logger.info(f"Checking path: {browser_path}")
    if os.path.exists(browser_path):
        logger.info(f"✓ Browser path exists: {browser_path}")
        # List what's in the directory
        try:
            contents = os.listdir(browser_path)
            logger.info(f"Directory contents: {contents}")
        except Exception as e:
            logger.error(f"Error listing directory: {e}")
    else:
        logger.warning(f"Browser path does not exist: {browser_path}")
        # Check parent directories
        parent = os.path.dirname(browser_path)
        logger.info(f"Checking parent: {parent} - exists: {os.path.exists(parent)}")
        if os.path.exists(parent):
            try:
                contents = os.listdir(parent)
                logger.info(f"Parent directory contents: {contents}")
            except Exception as e:
                logger.error(f"Error listing parent directory: {e}")
else:
    logger.warning("PLAYWRIGHT_BROWSERS_PATH environment variable is not set")
