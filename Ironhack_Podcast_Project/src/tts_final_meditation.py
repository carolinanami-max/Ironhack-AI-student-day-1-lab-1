import os
import re
import io
from dotenv import load_dotenv
from openai import OpenAI
from pydub import AudioSegment
from pydub.utils import make_chunks

load_dotenv()
client = OpenAI()

class FinalMeditationTTS:
    def __init__(self):
        self.client = client
        self.voice = "nova"
        self.speed = 0.75  # Slow for meditation
        self.pause_ms = 5000  # 5 seconds pause between affirmations
    
    def extract_affirmations(self, text):
        """Extract and clean individual affirmations"""
        # Split by ... or newlines
        lines = [line.strip() for line in text.split('\n')]
        affirmations = []
        
        for line in lines:
            if line and line != "...":
                # Clean up
                line = re.sub(r'^\s*[-•*]\s*', '', line)  # Remove bullet points
                line = re.sub(r'^\d+[\.\)]\s*', '', line)  # Remove numbers
                line = line.strip()
                
                if line:
                    # Ensure it starts with "I"
                    if line.lower().startswith("am "):
                        line = "I " + line
                    affirmations.append(line)
        
        print(f"  Extracted {len(affirmations)} affirmations")
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
            print(f"    ❌ Error generating affirmation: {e}")
            return None
    
    def create_meditation_with_pauses(self, affirmations, output_filename):
        """Create meditation audio with silent pauses between affirmations"""
        print("  Combining affirmations with pauses...")
        
        # Start with empty audio segment
        combined_audio = AudioSegment.silent(duration=0)
        
        for i, affirmation in enumerate(affirmations, 1):
            print(f"    {i}. {affirmation[:50]}...")
            
            # Generate audio for this affirmation
            audio_bytes = self.generate_affirmation_audio(affirmation)
            
            if audio_bytes:
                # Convert bytes to AudioSegment
                audio_segment = AudioSegment.from_file(
                    io.BytesIO(audio_bytes), 
                    format="mp3"
                )
                
                # Add this affirmation to combined audio
                combined_audio += audio_segment
                
                # Add silent pause (except after last one)
                if i < len(affirmations):
                    silence = AudioSegment.silent(duration=self.pause_ms)
                    combined_audio += silence
                    print(f"      Added {self.pause_ms/1000}s pause")
            else:
                print(f"      ⚠ Skipped due to error")
        
        # Export final audio
        combined_audio.export(output_filename, format="mp3")
        print(f"  ✅ Exported to {output_filename}")
        
        return True
    
    def generate_meditation_part(self, text, filename):
        """Generate the meditation/affirmations part with proper pauses"""
        print(f"\n🧘 GENERATING MEDITATION AFFIRMATIONS:")
        print(f"  Voice: {self.voice}")
        print(f"  Speed: {self.speed}")
        print(f"  Pause between affirmations: {self.pause_ms/1000} seconds")
        
        # Extract affirmations
        affirmations = self.extract_affirmations(text)
        
        if not affirmations:
            print("  ❌ No affirmations found")
            return False
        
        # Create output directory
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
        
        # Generate with pauses
        return self.create_meditation_with_pauses(affirmations, filename)
    
    def generate_other_part(self, text, filename, part_name):
        """Generate other parts (intro, opening, closing)"""
        print(f"\n📖 GENERATING {part_name.upper()}:")
        print(f"  Voice: {self.voice}")
        print(f"  Speed: {self.speed}")
        
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
                duration = len(AudioSegment.from_file(filename)) / 1000
                print(f"  ✅ Created: {filename}")
                print(f"     Size: {file_size} bytes")
                print(f"     Duration: ~{duration:.1f} seconds")
                return True
            else:
                print(f"  ❌ File not created")
                return False
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)[:100]}")
            return False

# Test with meditation affirmations
if __name__ == "__main__":
    print("=" * 60)
    print("FINAL MEDITATION WITH 5-SECOND PAUSES")
    print("=" * 60)
    
    # Read meditation text
    try:
        with open("../1. Input/Script Affirmations", 'r', encoding='utf-8') as f:
            meditation_text = f.read().strip()
        
        print(f"Original text: {len(meditation_text)} characters")
        
        # Create generator
        tts = FinalMeditationTTS()
        
        # Generate meditation with pauses
        output_file = "../meditation_with_pauses.mp3"
        success = tts.generate_meditation_part(meditation_text, output_file)
        
        if success:
            print("\n" + "=" * 60)
            print("✅ SUCCESS!")
            print("=" * 60)
            print("\nCreated: meditation_with_pauses.mp3")
            print("\nFeatures:")
            print("• Nova voice (soothing)")
            print(f"• {tts.pause_ms/1000}-second pauses between affirmations")
            print("• Slow pace (speed: 0.75)")
            print("• Listeners have time to repeat each affirmation")
        else:
            print("\n❌ Failed to create meditation")
            
    except ImportError as e:
        print(f"Error: {e}")
        print("\nMake sure pydub is installed:")
        print("pip install pydub")
    except Exception as e:
        print(f"Error: {e}")
