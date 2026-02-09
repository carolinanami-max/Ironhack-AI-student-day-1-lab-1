import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment - exactly like llm_processor.py
load_dotenv()

# Create client - exactly like llm_processor.py
client = OpenAI()

class TTSGenerator:
    def __init__(self, settings_file="../settings.json"):
        self.client = client
        
        # Load settings
        try:
            with open(settings_file, 'r') as f:
                self.settings = json.load(f)
        except FileNotFoundError:
            self.settings = {
                "voice": "alloy",
                "model": "tts-1", 
                "speed": 0.9
            }
    
    def generate_speech(self, text, filename, part_name=""):
        """Generate speech from text"""
        if part_name:
            print(f"Generating: {part_name}")
        
        print(f"Text: {text[:50]}..." if len(text) > 50 else f"Text: {text}")
        
        try:
            # Create directory if needed
            os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
            
            # Generate speech
            response = self.client.audio.speech.create(
                model=self.settings.get("model", "tts-1"),
                voice=self.settings.get("voice", "alloy"),
                input=text,
                speed=self.settings.get("speed", 0.9)
            )
            
            # Save to file
            response.stream_to_file(filename)
            
            # Check if file was created
            if os.path.exists(filename):
                print(f"✅ Created: {filename}")
                return True
            else:
                print(f"❌ Failed to create file")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

# Test when run directly
if __name__ == "__main__":
    print("Testing TTS Generator...")
    tts = TTSGenerator()
    success = tts.generate_speech(
        "Welcome to meditation practice.",
        "../test_output.mp3",
        "Test"
    )
    
    if success:
        print("🎉 TTS Generator is working!")
    else:
        print("❌ TTS Generator failed")
