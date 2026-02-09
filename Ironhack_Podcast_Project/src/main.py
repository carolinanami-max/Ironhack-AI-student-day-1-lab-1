# main.py - SIMPLE WORKING VERSION
import os
import sys
from tts_generator import TTSGenerator

def main():
    print("=" * 60)
    print("Meditation Podcast Creator")
    print("=" * 60)
    
    # Step 1: Initialize TTS Generator
    print("\n1. Initializing TTS Generator...")
    try:
        tts = TTSGenerator()
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        print("\nMake sure:")
        print("1. You have a .env file with OpenAI API key")
        print("2. You have installed: pip install openai python-dotenv")
        return
    
    # Step 2: Define meditation script
    print("\n2. Loading meditation script...")
    
    meditation_parts = {
        "intro": "Welcome to your five minute meditation practice. Find a comfortable position, sitting or lying down.",
        "opening": "Close your eyes gently. Take a deep breath in through your nose, and slowly exhale through your mouth. Release any tension you're holding.",
        "meditation": "With each breath, feel yourself becoming more relaxed. Notice the sensation of your breath moving in and out. If your mind wanders, gently bring it back to your breath. You are safe. You are at peace.",
        "closing": "Slowly begin to bring your awareness back to the room. Wiggle your fingers and toes. When you're ready, open your eyes. Carry this calm with you throughout your day."
    }
    
    print(f"   Loaded {len(meditation_parts)} meditation parts")
    
    # Step 3: Generate audio
    print("\n3. Generating audio files...")
    
    # Create output directory
    output_dir = "../output"
    os.makedirs(output_dir, exist_ok=True)
    
    audio_files = []
    
    for part_name, text in meditation_parts.items():
        filename = f"{output_dir}/{part_name}.mp3"
        print(f"\n   Processing: {part_name.upper()}")
        print(f"   Text: {text[:60]}...")
        
        success = tts.generate_speech(text, filename, part_name)
        
        if success:
            audio_files.append(filename)
            print(f"   ✅ Created: {filename}")
        else:
            print(f"   ❌ Failed: {part_name}")
    
    # Step 4: Summary
    print("\n" + "=" * 60)
    print("PROCESS COMPLETE")
    print("=" * 60)
    
    if audio_files:
        print(f"\n✅ Created {len(audio_files)} audio files:")
        for file in audio_files:
            print(f"   • {os.path.basename(file)}")
        
        print(f"\n📁 Files are in: {os.path.abspath(output_dir)}")
        print("\nNext: You can combine these files into one podcast using audio editing software.")
    else:
        print("\n❌ No audio files were created.")
        print("\nCheck:")
        print("1. Your OpenAI API key")
        print("2. Internet connection")
        print("3. File permissions")

if __name__ == "__main__":
    main()