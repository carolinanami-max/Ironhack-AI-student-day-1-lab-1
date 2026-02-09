import os
import requests
from dotenv import load_dotenv

load_dotenv('../.env')
api_key = os.getenv("OPENAI_API_KEY")

print(f"Key starts with: {api_key[:15]}...")

# Test a simple API call that should work
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

print("\n1. Testing models endpoint (should work for any valid key)...")
try:
    response = requests.get(
        "https://api.openai.com/v1/models",
        headers=headers,
        timeout=10
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Key is VALID for basic API access")
    else:
        print(f"   ❌ Key error: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ Connection error: {e}")

print("\n2. Testing chat completion (like your prompt project)...")
try:
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Say hello"}],
        "max_tokens": 5
    }
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=data,
        timeout=10
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Key works for chat completions")
    else:
        print(f"   ❌ Chat error: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ Connection error: {e}")
