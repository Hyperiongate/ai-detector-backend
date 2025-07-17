"""
Playwright configuration to ensure consistent browser paths
"""
import os
import logging

logger = logging.getLogger(__name__)

# Force remove any custom Playwright browser paths
if 'PLAYWRIGHT_BROWSERS_PATH' in os.environ:
    logger.warning(f"REMOVING PLAYWRIGHT_BROWSERS_PATH: {os.environ['PLAYWRIGHT_BROWSERS_PATH']}")
    del os.environ['PLAYWRIGHT_BROWSERS_PATH']

# This file should be imported before any Playwright usage
logger.info("Playwright config loaded - using default browser paths")
