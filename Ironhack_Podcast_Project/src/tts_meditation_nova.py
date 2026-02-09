import os
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

class MeditationTTSNova:
    def __init__(self):
        self.client = client
        self.voice = "nova"  # Your chosen soothing voice
        self.speed = 0.75    # Even slower for meditation
    
    def add_meditation_pauses(self, text, part_name):
        """Add proper pauses for meditation"""
        text = text.strip()
        
        # Fix missing "I" in affirmations
        if part_name == "meditation" and text.startswith("am "):
            text = "I " + text
        
        # For breathing instructions: add pause markers
        breathing_phrases = [
            "breathe in", "breathe out", "inhale", "exhale", 
            "take a deep breath", "hold your breath"
        ]
        
        for phrase in breathing_phrases:
            if phrase in text.lower():
                # Add [PAUSE] after breathing instructions
                pattern = re.compile(f'({phrase}[^.?!]*[.?!])', re.IGNORECASE)
                text = pattern.sub(r'\1 [PAUSE]', text)
        
        # For affirmations section: add pauses between each affirmation
        if part_name == "meditation":
            # Split by lines or ... markers
            lines = text.split('\n')
            processed_lines = []
            
            for line in lines:
                line = line.strip()
                if line and line != "...":
                    # Add pause marker after each affirmation
                    if not line.endswith('[PAUSE]'):
                        line = line + ' [PAUSE]'
                processed_lines.append(line)
            
            text = '\n'.join(processed_lines)
        
        # Replace ... with [PAUSE] markers (but keep some for pacing)
        text = text.replace('...', '[PAUSE]')
        
        return text
    
    def split_with_pauses(self, text):
        """Split text, keeping [PAUSE] markers for TTS"""
        # We'll keep [PAUSE] in text - TTS will say "pause" which we can edit out later
        # Or we can split and add actual pauses in audio editing
        return text
    
    def generate_speech(self, text, filename, part_name=""):
        """Generate speech with meditation pacing"""
        if part_name:
            print(f"\n🧘 {part_name.upper()}:")
        
        # Add meditation pauses
        prepared_text = self.add_meditation_pauses(text, part_name)
        
        word_count = len(prepared_text.split())
        print(f"   Words: {word_count}")
        print(f"   Voice: {self.voice}")
        print(f"   Speed: {self.speed}")
        print(f"   Output: {filename}")
        
        try:
            os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
            
            # For very long text, split it
            if len(prepared_text) > 2000:
                print("   Text is long, splitting...")
                # Simple split by sentences
                sentences = re.split(r'(?<=[.!?])\s+', prepared_text)
                chunks = []
                current_chunk = ""
                
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) < 1800:
                        current_chunk += " " + sentence if current_chunk else sentence
                    else:
                        if current_chunk:
                            chunks.append(current_chunk)
                        current_chunk = sentence
                
                if current_chunk:
                    chunks.append(current_chunk)
                
                print(f"   Split into {len(chunks)} chunks")
                
                # This is complex - for now, let's try without splitting
                # We'll use the full text and see if it works
            
            # Generate speech
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=self.voice,
                input=prepared_text,
                speed=self.speed
            )
            
            # Save file
            response.stream_to_file(filename)
            
            if os.path.exists(filename):
                file_size = os.path.getsize(filename)
                duration_est = file_size / 16000  # Rough estimate
                print(f"   ✅ Created ({file_size} bytes)")
                print(f"   ⏱️  Estimated: {duration_est:.1f} seconds")
                return True
            else:
                print(f"   ❌ Failed to create file")
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:150]}")
            return False

# Test with meditation affirmations
if __name__ == "__main__":
    print("=" * 60)
    print("TESTING NOVA VOICE WITH MEDITATION PAUSES")
    print("=" * 60)
    
    # Read meditation text
    try:
        with open("../1. Input/Script Affirmations", 'r', encoding='utf-8') as f:
            meditation_text = f.read().strip()
        
        print(f"Original text: {len(meditation_text)} characters")
        
        # Create generator
        tts = MeditationTTSNova()
        
        # Generate test
        output_file = "../test_nova_meditation.mp3"
        success = tts.generate_speech(meditation_text, output_file, "meditation")
        
        if success:
            print("\n✅ Test successful! Listen to test_nova_meditation.mp3")
            print("\nCheck if:")
            print("1. Voice is soothing (nova)")
            print("2. There are pauses between affirmations")
            print("3. Pace is slow enough for meditation")
        else:
            print("\n❌ Test failed")
            
    except Exception as e:
        print(f"Error: {e}")
