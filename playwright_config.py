"""
Playwright configuration to ensure consistent browser paths
"""
import os
import logging

logger = logging.getLogger(__name__)

# Just log the current state - don't modify anything
browser_path = os.environ.get('PLAYWRIGHT_BROWSERS_PATH', 'Not set')
logger.info(f"Playwright config loaded - PLAYWRIGHT_BROWSERS_PATH: {browser_path}")

# Optional: Verify the path exists (for debugging)
if browser_path != 'Not set' and os.path.exists(browser_path):
    logger.info(f"✓ Browser path exists: {browser_path}")
else:
    logger.warning(f"Browser path does not exist or is not set: {browser_path}")
