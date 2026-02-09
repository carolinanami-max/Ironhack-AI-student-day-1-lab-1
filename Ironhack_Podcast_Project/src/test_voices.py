import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

# Soothing voice options for meditation
voices = ["sage", "shimmer", "nova", "echo", "alloy"]

test_text = "Take a deep breath in. Hold. And breathe out slowly."

print("=" * 60)
print("TESTING SOOTHING VOICES FOR MEDITATION")
print("=" * 60)

for voice in voices:
    print(f"\nTesting voice: {voice}")
    
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=test_text,
            speed=0.75  # Extra slow for meditation
        )
        
        filename = f"../voice_test_{voice}.mp3"
        response.stream_to_file(filename)
        
        if os.path.exists(filename):
            file_size = os.path.getsize(filename)
            print(f"  ✅ Created: {filename} ({file_size} bytes)")
        else:
            print(f"  ❌ Failed to create")
            
    except Exception as e:
        print(f"  ❌ Error: {str(e)[:100]}")

print("\n" + "=" * 60)
print("Listen to the voice_test_*.mp3 files")
print("Choose the most soothing voice for your meditation.")
print("=" * 60)
