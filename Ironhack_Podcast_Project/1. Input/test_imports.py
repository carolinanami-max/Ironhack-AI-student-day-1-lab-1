# test_imports.py
import os
import sys

print("Testing imports...")
print(f"Current directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

# Try to import dotenv
try:
    from dotenv import load_dotenv
    print("✓ dotenv imported successfully")
except ImportError as e:
    print(f"✗ Error importing dotenv: {e}")

# Try to import llm_processor
try:
    from llm_processor import llm_processor
    print("✓ llm_processor imported successfully")
except ImportError as e:
    print(f"✗ Error importing llm_processor: {e}")
    print("Let's check if the file exists...")
    print(f"llm_processor.py exists: {os.path.exists('llm_processor.py')}")