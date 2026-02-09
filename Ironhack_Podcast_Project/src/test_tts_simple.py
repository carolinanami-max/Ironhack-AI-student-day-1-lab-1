from dotenv import load_dotenv
from openai import OpenAI

print("Starting simple test...")

# Load environment
load_dotenv()

# Create client
client = OpenAI()

print("Client created")

# Try TTS
try:
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input="Hello test",
        speed=0.9
    )
    
    # Save file
    response.stream_to_file("../test_simple.mp3")
    
    print("SUCCESS: test_simple.mp3 created")
    
except Exception as e:
    print(f"ERROR: {e}")
