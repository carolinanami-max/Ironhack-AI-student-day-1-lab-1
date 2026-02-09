import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

def regenerate_part(text, output_file, part_name, speed=1.0):
    """Regenerate a part at specified speed"""
    print(f"\n🔧 Regenerating {part_name} at speed {speed}:")
    print(f"   Output: {output_file}")
    
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=text,
            speed=speed
        )
        
        # Create directory if needed
        os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
        
        response.stream_to_file(output_file)
        
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"   ✅ Created ({file_size} bytes)")
            return True
        else:
            print(f"   ❌ Failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("REGENERATING PARTS AT SPEED 1.0")
    print("=" * 60)
    
    # Create output directory
    output_dir = "../ironhack_mindfulness_podcast_final"
    os.makedirs(output_dir, exist_ok=True)
    print(f"\nOutput directory: {output_dir}")
    
    # Script files to regenerate
    script_files = {
        "intro": "../1. Input/Script Intro",
        "opening": "../1. Input/Script Opening",
        "closing": "../1. Input/Script Closing"
    }
    
    # Regenerate each part at speed 1.0
    for name, filepath in script_files.items():
        print(f"\nProcessing {name}...")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read().strip()
            
            output_file = os.path.join(output_dir, f"{name}.mp3")
            regenerate_part(text, output_file, name, speed=1.0)
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Copy affirmations (already at speed 0.75)
    print("\n" + "=" * 60)
    print("COPYING AFFIRMATIONS (keeping speed 0.75)")
    print("=" * 60)
    
    import shutil
    import glob
    
    # Copy all affirmation files
    affirmation_files = sorted(glob.glob("../meditation_parts/affirmation_*.mp3"))
    
    if affirmation_files:
        print(f"\nFound {len(affirmation_files)} affirmation files")
        
        for src_file in affirmation_files:
            filename = os.path.basename(src_file)
            dst_file = os.path.join(output_dir, filename)
            
            try:
                shutil.copy2(src_file, dst_file)
                print(f"  ✅ Copied: {filename}")
            except Exception as e:
                print(f"  ❌ Failed to copy {filename}: {e}")
    else:
        print("❌ No affirmation files found!")
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    print(f"\nFiles in '{output_dir}':")
    all_files = sorted(os.listdir(output_dir))
    for file in all_files:
        if file.endswith('.mp3'):
            filepath = os.path.join(output_dir, file)
            size = os.path.getsize(filepath)
            print(f"  • {file} ({size/1000:.0f} KB)")
    
    print(f"\nTotal: {len(all_files)} MP3 files ready for combining")

if __name__ == "__main__":
    main()
