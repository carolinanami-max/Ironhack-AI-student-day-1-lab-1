import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables - EXACTLY like llm_processor.py
load_dotenv()

# Create OpenAI client - EXACTLY like llm_processor.py
client = OpenAI()

class TTSGenerator:
    def __init__(self, settings_file="../settings.json"):
        """Initialize TTS Generator"""
        self.client = client
        
        # Load settings from JSON file
        try:
            with open(settings_file, 'r') as f:
                self.settings = json.load(f)
        except FileNotFoundError:
            # Default settings if file not found
            self.settings = {
                "voice": "alloy",
                "model": "tts-1",
                "speed": 0.9
            }
    
    def generate_speech(self, text, filename, part_name=""):
        """Convert text to speech"""
        if part_name:
            print(f"\n🎤 Generating: {part_name}")
        
        print(f"   Text: {text[:50]}..." if len(text) > 50 else f"   Text: {text}")
        print(f"   Output: {filename}")
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
            
            # Generate speech using OpenAI TTS
            response = self.client.audio.speech.create(
                model=self.settings.get("model", "tts-1"),
                voice=self.settings.get("voice", "alloy"),
                input=text,
                speed=self.settings.get("speed", 0.9)
            )
            
            # Save the audio file
            response.stream_to_file(filename)
            
            # Verify file was created
            if os.path.exists(filename):
                file_size = os.path.getsize(filename)
                print(f"   ✅ Success! Created {filename} ({file_size} bytes)")
                return True
            else:
                print(f"   ❌ Error: File was not created")
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False

# Simple test when run directly
if __name__ == "__main__":
    print("=" * 50)
    print("Testing TTS Generator")
    print("=" * 50)
    
    # Create TTS generator
    tts = TTSGenerator()
    
    # Test meditation text
    test_text = "Welcome to your meditation practice. Find a comfortable position."
    test_file = "../test_meditation_final.mp3"
    
    # Generate speech
    success = tts.generate_speech(test_text, test_file, "Test Meditation")
    
    if success:
        print("\n" + "=" * 50)
        print("🎉 TTS GENERATOR IS WORKING!")
        print("=" * 50)
        print("\nYou can now use this in your main.py to create")
        print("your meditation podcast!")
    else:
        print("\n" + "=" * 50)
        print("❌ Test failed")
        print("=" * 50)
