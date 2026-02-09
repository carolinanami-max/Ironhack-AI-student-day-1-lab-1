import os
import re
import time
from dotenv import load_dotenv
from openai import OpenAI
from pydub import AudioSegment
import io

load_dotenv()
client = OpenAI()

class MeditationTTSWithPauses:
    def __init__(self):
        self.client = client
        self.voice = "nova"
        self.speed = 0.75
    
    def extract_affirmations(self, text):
        """Extract individual affirmations from meditation text"""
        # Split by ... or newlines
        lines = text.split('\n')
        affirmations = []
        
        for line in lines:
            line = line.strip()
            if line and line != "...":
                # Clean up the line
                line = re.sub(r'^\d+[\.\)]\s*', '', line)  # Remove numbers like "1. "
                line = line.strip()
                if line:
                    # Ensure it starts with "I"
                    if line.lower().startswith("am "):
                        line = "I " + line
                    affirmations.append(line)
        
        print(f"  Found {len(affirmations)} affirmations")
        for i, aff in enumerate(affirmations[:3], 1):
            print(f"    {i}. {aff[:50]}...")
        if len(affirmations) > 3:
            print(f"    ... and {len(affirmations)-3} more")
        
        return affirmations
    
    def generate_affirmation_audio(self, text):
        """Generate audio for a single affirmation"""
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=self.voice,
                input=text,
                speed=self.speed
            )
            return response.content
        except Exception as e:
            print(f"    ❌ Error generating '{text[:30]}...': {e}")
            return None
    
    def add_silence(self, audio_bytes, silence_duration_ms=4000):
        """Add silence to audio (4 seconds for repeating)"""
        try:
            # Load audio
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
            
            # Create silence
            silence = AudioSegment.silent(duration=silence_duration_ms)
            
            # Combine: affirmation + silence for repeating
            combined = audio + silence
            
            # Export back to bytes
            buffer = io.BytesIO()
            combined.export(buffer, format="mp3")
            return buffer.getvalue()
            
        except Exception as e:
            print(f"    ⚠ Could not add silence: {e}")
            # Return original if we can't process
            return audio_bytes
    
    def combine_audio_files(self, audio_chunks, output_filename):
        """Combine multiple audio chunks into one file"""
        try:
            # This is complex without pydub installed
            # For now, we'll write a simple version
            
            # If pydub is not available, we'll use a different approach
            print("  Combining audio segments...")
            
            # Write all audio to a file
            with open(output_filename, 'wb') as f:
                for chunk in audio_chunks:
                    if chunk:
                        f.write(chunk)
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error combining audio: {e}")
            return False
    
    def generate_meditation_with_pauses(self, text, filename, part_name=""):
        """Special method for meditation part with real pauses"""
        print(f"\n🧘 {part_name.upper()}:")
        print(f"  Generating with REAL pauses for repetition...")
        
        # Extract individual affirmations
        affirmations = self.extract_affirmations(text)
        
        if not affirmations:
            print("  ❌ No affirmations found")
            return False
        
        all_audio_chunks = []
        
        # Generate each affirmation separately
        for i, affirmation in enumerate(affirmations, 1):
            print(f"  Affirmation {i}/{len(affirmations)}: '{affirmation[:40]}...'")
            
            # Generate audio for this affirmation
            audio_bytes = self.generate_affirmation_audio(affirmation)
            
            if audio_bytes:
                # Add silence after each affirmation for repetition
                audio_with_silence = self.add_silence(audio_bytes, 4000)  # 4 seconds
                all_audio_chunks.append(audio_with_silence)
                print(f"    ✅ Generated with 4-second pause")
            else:
                print(f"    ❌ Failed to generate")
        
        # Try to save combined audio
        try:
            with open(filename, 'wb') as f:
                for chunk in all_audio_chunks:
                    f.write(chunk)
            
            if os.path.exists(filename):
                file_size = os.path.getsize(filename)
                print(f"\n  ✅ Created: {filename} ({file_size} bytes)")
                
                # Estimate duration
                # Each affirmation ~3 seconds + 4 seconds pause = ~7 seconds each
                estimated_seconds = len(affirmations) * 7
                print(f"  ⏱️  Estimated: {estimated_seconds} seconds ({estimated_seconds/60:.1f} minutes)")
                return True
                
        except Exception as e:
            print(f"  ❌ Error saving: {e}")
        
        return False
    
    def generate_speech(self, text, filename, part_name=""):
        """Generate speech - special handling for meditation"""
        if part_name == "meditation":
            return self.generate_meditation_with_pauses(text, filename, part_name)
        
        # For other parts (intro, opening, closing)
        if part_name:
            print(f"\n📖 {part_name.upper()}:")
        
        print(f"  Words: {len(text.split())}")
        print(f"  Voice: {self.voice}")
        
        try:
            os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
            
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=self.voice,
                input=text,
                speed=self.speed
            )
            
            response.stream_to_file(filename)
            
            if os.path.exists(filename):
                file_size = os.path.getsize(filename)
                print(f"  ✅ Created ({file_size} bytes)")
                return True
            else:
                print(f"  ❌ Failed")
                return False
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)[:100]}")
            return False

# Test with meditation affirmations
if __name__ == "__main__":
    print("=" * 60)
    print("TESTING WITH REAL PAUSES FOR REPETITION")
    print("=" * 60)
    
    # Read meditation text
    try:
        with open("../1. Input/Script Affirmations", 'r', encoding='utf-8') as f:
            meditation_text = f.read().strip()
        
        print(f"Original text: {len(meditation_text)} characters")
        
        # Create generator
        tts = MeditationTTSWithPauses()
        
        # Generate test
        output_file = "../test_with_real_pauses.mp3"
        success = tts.generate_speech(meditation_text, output_file, "meditation")
        
        if success:
            print("\n✅ Test successful! Listen to test_with_real_pauses.mp3")
            print("\nEach affirmation should have 4 seconds of silence after it")
            print("for listeners to repeat.")
        else:
            print("\n❌ Test failed")
            
    except Exception as e:
        print(f"Error: {e}")
