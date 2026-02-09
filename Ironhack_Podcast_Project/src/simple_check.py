print("=== SIMPLE CHECK ===")
print("Testing if we're using the right Python...")

import sys
print(f"Python path: {sys.executable}")

# Check if it's the conda Python
if "miniconda3" in sys.executable:
    print("✅ GOOD: Using conda Python")
else:
    print("⚠ WARNING: Not using conda Python")
    print("Try running with: python simple_check.py")

# Try to import packages
try:
    import requests
    print("✅ requests is installed")
except:
    print("❌ requests NOT installed")

print("=== CHECK COMPLETE ===")
