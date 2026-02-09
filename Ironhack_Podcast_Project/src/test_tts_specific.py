import os
import requests
from dotenv import load_dotenv

load_dotenv('../.env')
api_key = os.getenv("OPENAI_API_KEY")

print("Testing TTS API specifically...")

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Try TTS with minimal request
data = {
    "model": "tts-1",
    "input": "test",
    "voice": "alloy"
}

try:
    response = requests.post(
        "https://api.openai.com/v1/audio/speech",
        headers=headers,
        json=data,
        timeout=10
    )
    
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ TTS API works!")
    elif response.status_code == 401:
        print("❌ 401 Unauthorized")
        print(f"Error details: {response.text}")
        
        # Check error message more carefully
        error_data = response.json()
        if 'error' in error_data:
            error_msg = error_data['error']
            print(f"Error message: {error_msg}")
            
    elif response.status_code == 403:
        print("❌ 403 Forbidden - TTS API might be blocked for your account")
    elif response.status_code == 429:
        print("⚠ 429 Rate Limited - Too many requests")
    else:
        print(f"⚠ Unexpected status: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
except Exception as e:
    print(f"❌ Connection error: {e}")
    import traceback
    traceback.print_exc()
