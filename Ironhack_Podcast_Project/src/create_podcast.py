import os
from tts_generator import TTSGenerator

print("=" * 60)
print("CREATING MEDITATION PODCAST")
print("=" * 60)

# Step 1: Create TTS generator
print("\n1. Initializing TTS Generator...")
tts = TTSGenerator()
print("   ✅ TTS Generator ready")

# Step 2: Define script file paths (without .txt extension)
print("\n2. Setting up meditation scripts...")
script_files = {
    "intro": "../1. Input/Script Intro",
    "opening": "../1. Input/Script Opening",
    "meditation": "../1. Input/Script Affirmations",
    "closing": "../1. Input/Script Closing"
}

# Step 3: Create output folder
output_dir = "../output"
os.makedirs(output_dir, exist_ok=True)
print(f"   ✅ Output folder: {output_dir}")

# Step 4: Process each script
print("\n3. Processing scripts...")
print("   (This may take a few minutes)")

for name, filepath in script_files.items():
    print(f"\n   {name.upper()}:")
    
    # Read the script
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read().strip()
        
        print(f"     Read {len(text)} characters")
        
        # Generate audio
        output_file = f"{output_dir}/{name}.mp3"
        success = tts.generate_speech(text, output_file, name)
        
        if success:
            print(f"     ✅ Created: {name}.mp3")
        else:
            print(f"     ❌ Failed to create: {name}.mp3")
            
    except Exception as e:
        print(f"     ❌ Error: {e}")

# Step 5: Summary
print("\n" + "=" * 60)
print("PODCAST CREATION COMPLETE")
print("=" * 60)
print("\nCheck the 'output' folder for your meditation podcast MP3 files!")
print(f"Location: {os.path.abspath(output_dir)}")
