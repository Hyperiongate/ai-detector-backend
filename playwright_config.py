"""
Playwright configuration to ensure consistent browser paths
"""
import os

print("=== PLAYWRIGHT CONFIG STARTUP ===")

# Check the environment variable
browser_path = os.environ.get('PLAYWRIGHT_BROWSERS_PATH', 'Not set')
print(f"PLAYWRIGHT_BROWSERS_PATH: {browser_path}")

# List all environment variables that contain 'PLAYWRIGHT'
print("\nAll PLAYWRIGHT-related env vars:")
for key, value in os.environ.items():
    if 'PLAYWRIGHT' in key.upper():
        print(f"  {key}: {value}")

# Check if the path exists
if browser_path != 'Not set':
    exists = os.path.exists(browser_path)
    print(f"\nPath exists: {exists}")
    
    if not exists:
        # Check parent directories
        parts = browser_path.split('/')
        for i in range(len(parts), 0, -1):
            check_path = '/'.join(parts[:i])
            if check_path and os.path.exists(check_path):
                print(f"Parent exists: {check_path}")
                try:
                    contents = os.listdir(check_path)
                    print(f"  Contents: {contents[:5]}...")  # First 5 items
                except Exception as e:
                    print(f"  Error listing: {e}")
                break

print("=== END PLAYWRIGHT CONFIG ===\n")
