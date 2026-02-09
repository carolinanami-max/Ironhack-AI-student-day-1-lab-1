import os
import json
import time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

class MeditationTTSGenerator:
    def __init__(self, settings_file="../settings.json"):
        self.client = client
        try:
            with open(settings_file, 'r') as f:
                self.settings = json.load(f)
        except FileNotFoundError:
            # Optimized for meditation
            self.settings = {
                "voice": "alloy",      # Calm voice
                "model": "tts-1",
                "speed": 0.8,          # Slower pace for meditation
                "chunk_size": 2000     # Process in chunks to avoid cutoff
            }
    
    def split_into_chunks(self, text, max_chars=2000):
        """Split text into chunks that won't get cut off"""
        # Split by sentences first
        sentences = []
        current_sentence = ""
        
        for char in text:
            current_sentence += char
            if char in '.!?':
                sentences.append(current_sentence.strip())
                current_sentence = ""
        
        if current_sentence:
            sentences.append(current_sentence.strip())
        
        # Group sentences into chunks
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 < max_chars:
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def generate_speech(self, text, filename, part_name=""):
        """Generate speech with proper meditation pacing"""
        if part_name:
            print(f"\n🎤 Generating: {part_name}")
        
        print(f"   Text length: {len(text)} characters")
        print(f"   Estimated: {len(text.split())} words")
        print(f"   Output: {filename}")
        
        try:
            os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
            
            # Process in chunks to ensure nothing gets cut off
            chunks = self.split_into_chunks(text)
            
            if len(chunks) > 1:
                print(f"   Processing in {len(chunks)} chunks...")
            
            all_audio = bytearray()
            
            for i, chunk in enumerate(chunks):
                print(f"   Chunk {i+1}/{len(chunks)}: {len(chunk)} chars")
                
                # Replace ... with . to avoid TTS issues, but keep meaning
                # We'll handle pauses differently
                chunk_for_tts = chunk.replace('...', '.')
                
                response = self.client.audio.speech.create(
                    model=self.settings.get("model", "tts-1"),
                    voice=self.settings.get("voice", "alloy"),
                    input=chunk_for_tts,
                    speed=self.settings.get("speed", 0.8)
                )
                
                # Get audio content
                audio_content = response.content
                all_audio.extend(audio_content)
                
                # Small delay between chunks
                if i < len(chunks) - 1:
                    time.sleep(0.5)
            
            # Save combined audio
            with open(filename, 'wb') as f:
                f.write(all_audio)
            
            # Verify file
            if os.path.exists(filename):
                file_size = os.path.getsize(filename)
                duration_est = file_size / 16000  # Rough estimate
                print(f"   ✅ Created: {filename} ({file_size} bytes)")
                print(f"   ⏱️  Estimated duration: {duration_est:.1f} seconds")
                return True
            else:
                print(f"   ❌ File not created")
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:200]}")
            return False

# Test with one file
if __name__ == "__main__":
    print("=" * 60)
    print("TESTING MEDITATION TTS GENERATOR")
    print("=" * 60)
    
    # Test with meditation file
    test_file = "../1. Input/Script Affirmations"
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            test_text = f.read().strip()
        
        # Fix missing "I" at beginning
        if test_text.startswith("am "):
            test_text = "I " + test_text
        
        print(f"Test text: {len(test_text)} characters")
        print(f"Preview: {test_text[:100]}...")
        
        # Create generator
        tts = MeditationTTSGenerator()
        
        # Generate
        output_file = "../test_meditation_fixed.mp3"
        success = tts.generate_speech(test_text, output_file, "Test Meditation")
        
        if success:
            print("\n✅ TEST SUCCESSFUL!")
        else:
            print("\n❌ TEST FAILED")
            
    except Exception as e:
        print(f"Error: {e}")
