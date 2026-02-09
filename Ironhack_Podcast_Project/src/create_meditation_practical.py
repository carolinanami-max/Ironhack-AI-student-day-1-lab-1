import os
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

class PracticalMeditationCreator:
    def __init__(self):
        self.client = client
        self.voice = "nova"
        self.speed = 0.75
    
    def extract_affirmations(self, text):
        """Extract and clean individual affirmations"""
        lines = [line.strip() for line in text.split('\n')]
        affirmations = []
        
        for line in lines:
            if line and line != "...":
                # Clean up
                line = re.sub(r'^\s*[-•*]\s*', '', line)
                line = line.strip()
                
                if line:
                    # Ensure it starts with "I"
                    if line.lower().startswith("am "):
                        line = "I " + line
                    affirmations.append(line)
        
        return affirmations
    
    def generate_separate_affirmations(self, text, output_dir):
        """Generate each affirmation as separate MP3 file"""
        affirmations = self.extract_affirmations(text)
        
        if not affirmations:
            print("  ❌ No affirmations found")
            return []
        
        print(f"  Generating {len(affirmations)} separate affirmation files...")
        
        generated_files = []
        
        for i, affirmation in enumerate(affirmations, 1):
            print(f"    {i}. {affirmation[:50]}...")
            
            try:
                output_file = os.path.join(output_dir, f"affirmation_{i:02d}.mp3")
                
                response = self.client.audio.speech.create(
                    model="tts-1",
                    voice=self.voice,
                    input=affirmation,
                    speed=self.speed
                )
                
                response.stream_to_file(output_file)
                
                if os.path.exists(output_file):
                    generated_files.append(output_file)
                    print(f"      ✅ Saved as affirmation_{i:02d}.mp3")
                else:
                    print(f"      ❌ Failed to save")
                    
            except Exception as e:
                print(f"      ❌ Error: {str(e)[:80]}")
        
        return generated_files
    
    def generate_continuous_version(self, text, output_file):
        """Generate continuous version (for reference)"""
        try:
            # Clean up text for continuous version
            lines = [line.strip() for line in text.split('\n')]
            cleaned_lines = []
            
            for line in lines:
                if line and line != "...":
                    if line.lower().startswith("am "):
                        line = "I " + line
                    cleaned_lines.append(line)
            
            continuous_text = ". ".join(cleaned_lines)
            
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=self.voice,
                input=continuous_text,
                speed=self.speed
            )
            
            response.stream_to_file(output_file)
            
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                print(f"  ✅ Continuous version: {output_file} ({file_size} bytes)")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False
    
    def generate_other_part(self, text, output_file, part_name):
        """Generate intro, opening, closing parts"""
        print(f"\n📖 {part_name.upper()}:")
        
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=self.voice,
                input=text,
                speed=self.speed
            )
            
            response.stream_to_file(output_file)
            
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                print(f"  ✅ Created: {output_file} ({file_size} bytes)")
                return True
            else:
                print(f"  ❌ Failed to create")
                return False
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False

def main():
    print("=" * 70)
    print("PRACTICAL MEDITATION PODCAST CREATOR")
    print("=" * 70)
    
    # Create output directories
    meditation_dir = "../meditation_parts"
    final_dir = "../final_meditation"
    
    os.makedirs(meditation_dir, exist_ok=True)
    os.makedirs(final_dir, exist_ok=True)
    
    # Script files
    script_files = {
        "intro": "../1. Input/Script Intro",
        "opening": "../1. Input/Script Opening",
        "meditation": "../1. Input/Script Affirmations",
        "closing": "../1. Input/Script Closing"
    }
    
    # Create generator
    creator = PracticalMeditationCreator()
    
    print(f"\nVoice: {creator.voice}")
    print(f"Speed: {creator.speed} (slow for meditation)")
    print(f"\nOutput folders:")
    print(f"  • {os.path.abspath(meditation_dir)} - Separate affirmation files")
    print(f"  • {os.path.abspath(final_dir)} - Final combined parts")
    
    # Process each part
    print("\n" + "=" * 70)
    print("GENERATING PODCAST PARTS")
    print("=" * 70)
    
    all_parts = {}
    
    for name, filepath in script_files.items():
        print(f"\nProcessing {name}...")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read().strip()
            
            if name == "meditation":
                # Special handling for meditation/affirmations
                print(f"  This is the affirmations section")
                print(f"  Generating separate files for each affirmation...")
                
                # Generate separate affirmation files
                affirmation_files = creator.generate_separate_affirmations(text, meditation_dir)
                
                # Also generate continuous version for reference
                continuous_file = os.path.join(final_dir, "meditation_continuous.mp3")
                creator.generate_continuous_version(text, continuous_file)
                
                all_parts[name] = {
                    "type": "affirmations",
                    "files": affirmation_files,
                    "continuous": continuous_file
                }
                
            else:
                # Regular parts (intro, opening, closing)
                output_file = os.path.join(final_dir, f"{name}.mp3")
                success = creator.generate_other_part(text, output_file, name)
                
                if success:
                    all_parts[name] = {
                        "type": "regular",
                        "file": output_file
                    }
                
        except Exception as e:
            print(f"  ❌ Error processing {name}: {e}")
    
    # Create instructions
    print("\n" + "=" * 70)
    print("INSTRUCTIONS FOR FINAL PODCAST")
    print("=" * 70)
    
    print("\n✅ FILES CREATED:")
    
    # List all files
    print("\nIn 'final_meditation' folder:")
    for name, info in all_parts.items():
        if name != "meditation":
            if os.path.exists(info["file"]):
                print(f"  • {name}.mp3")
    
    if "meditation" in all_parts:
        print(f"  • meditation_continuous.mp3 (reference - no pauses)")
    
    print("\nIn 'meditation_parts' folder (for affirmations):")
    if "meditation" in all_parts:
        aff_files = all_parts["meditation"]["files"]
        print(f"  • {len(aff_files)} separate affirmation files")
        print(f"    (affirmation_01.mp3, affirmation_02.mp3, etc.)")
    
    print("\n" + "=" * 70)
    print("HOW TO CREATE THE FINAL MEDITATION:")
    print("=" * 70)
    
    print("\n1. FOR AFFIRMATIONS (meditation part):")
    print("   Use audio editing software (Audacity, GarageBand, etc.):")
    print("   a. Import all affirmation_*.mp3 files")
    print("   b. Add 4-5 seconds of silence between each")
    print("   c. Export as 'meditation_with_pauses.mp3'")
    
    print("\n2. COMBINE ALL PARTS:")
    print("   In audio editor, combine in this order:")
    print("   1. intro.mp3")
    print("   2. opening.mp3")
    print("   3. meditation_with_pauses.mp3 (your edited version)")
    print("   4. closing.mp3")
    
    print("\n3. FINAL TOUCHES:")
    print("   • Adjust volume levels if needed")
    print("   • Add background music (optional)")
    print("   • Add fade in/out (optional)")
    
    print("\n" + "=" * 70)
    print("ESTIMATED TIMING:")
    print("=" * 70)
    
    # Estimate times
    total_estimates = 0
    
    for name, info in all_parts.items():
        if name == "meditation":
            # Estimate: each affirmation ~3s + 5s pause = 8s each
            if "files" in info:
                num_affirmations = len(info["files"])
                meditation_time = num_affirmations * 8
                print(f"\nMeditation (affirmations):")
                print(f"  • {num_affirmations} affirmations")
                print(f"  • Each: ~3s speech + 5s pause = 8s")
                print(f"  • Total: ~{meditation_time}s ({meditation_time/60:.1f} min)")
                total_estimates += meditation_time
        else:
            # Estimate regular parts
            if "file" in info and os.path.exists(info["file"]):
                file_size = os.path.getsize(info["file"])
                est_time = file_size / 16000  # Rough estimate
                print(f"\n{name}: ~{est_time:.1f}s")
                total_estimates += est_time
    
    print(f"\nTotal estimated podcast length: {total_estimates/60:.1f} minutes")
    
    print("\n" + "=" * 70)
    print("🎧 Your meditation podcast components are ready!")
    print("=" * 70)

if __name__ == "__main__":
    main()
