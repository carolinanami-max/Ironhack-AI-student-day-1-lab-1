# Simple test - works like llm_processor.py
from dotenv import load_dotenv
from openai import OpenAI

# Load environment exactly like llm_processor.py
load_dotenv()

# Create client exactly like llm_processor.py
client = OpenAI()

print("Testing TTS...")

try:
    # Try to generate speech
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input="Hello, this is a test.",
        speed=0.9
    )
    
    # Save to file
    response.stream_to_file("../simple_test.mp3")
    
    print("✅ SUCCESS! Created simple_test.mp3")
    
except Exception as e:
    print(f"❌ Error: {e}")
