import os
import glob
import subprocess
import sys

print("=" * 70)
print("COMBINING FINAL MEDITATION PODCAST")
print("=" * 70)

# Define paths
source_dir = "../ironhack_mindfulness_podcast_final"
output_file = os.path.join(source_dir, "Ironhack_Mindfulness_Podcast_Final.mp3")

print(f"Source directory: {os.path.abspath(source_dir)}")
print(f"Output file: {os.path.abspath(output_file)}")

# Check if ffmpeg is installed
def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

if not check_ffmpeg():
    print("\n❌ ffmpeg is not installed!")
    print("\nPlease install ffmpeg:")
    print("  brew install ffmpeg")
    print("\nOr use Audacity for manual combining (recommended for pauses).")
    sys.exit(1)

# Get files in EXACT order
print("\n" + "=" * 70)
print("FILES IN ORDER:")
print("=" * 70)

files_in_order = []

# 1. Intro (speed 1.0)
intro_file = os.path.join(source_dir, "intro.mp3")
if os.path.exists(intro_file):
    files_in_order.append(intro_file)
    print("1. intro.mp3")

# 2. Opening (note: named opening075.mp3!)
opening_file = os.path.join(source_dir, "opening075.mp3")
if os.path.exists(opening_file):
    files_in_order.append(opening_file)
    print("2. opening075.mp3")

# 3. Affirmations 1-19 (speed 0.75)
affirmation_files = sorted(glob.glob(os.path.join(source_dir, "affirmation_*.mp3")))
for i, file in enumerate(affirmation_files, 1):
    files_in_order.append(file)
    print(f"{i+2}. {os.path.basename(file)}")

# 4. Closing (speed 1.0)
closing_file = os.path.join(source_dir, "closing.mp3")
if os.path.exists(closing_file):
    files_in_order.append(closing_file)
    print(f"{len(files_in_order)}. closing.mp3")

print(f"\n✅ Total files: {len(files_in_order)}")

# Create file list for ffmpeg
filelist_path = os.path.join(source_dir, "ffmpeg_filelist.txt")
with open(filelist_path, 'w') as f:
    for file in files_in_order:
        f.write(f"file '{os.path.abspath(file)}'\n")

print(f"\n📝 Created ffmpeg file list: {filelist_path}")

# Combine using ffmpeg
print("\n" + "=" * 70)
print("COMBINING FILES...")
print("=" * 70)

try:
    cmd = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", filelist_path,
        "-c", "copy",
        output_file
    ]
    
    print(f"Running ffmpeg command...")
    print(f"Output: {os.path.basename(output_file)}")
    
    # Run with progress
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            duration_seconds = file_size / 16000  # Rough estimate
            
            print(f"\n🎉 SUCCESS!")
            print(f"   File: {os.path.basename(output_file)}")
            print(f"   Size: {file_size/1000000:.1f} MB")
            print(f"   Duration: ~{duration_seconds/60:.1f} minutes")
            
            # Show breakdown
            print(f"\n📊 Breakdown:")
            print(f"   • intro.mp3 (speed 1.0)")
            print(f"   • opening075.mp3 (speed 0.75)")
            print(f"   • 19 affirmations (speed 0.75)")
            print(f"   • closing.mp3 (speed 1.0)")
            
        else:
            print(f"\n❌ File was not created")
    else:
        print(f"\n❌ ffmpeg error:")
        if result.stderr:
            print(result.stderr[:500])
        
except Exception as e:
    print(f"\n❌ Error: {e}")

# AUDACITY INSTRUCTIONS (for adding pauses)
print("\n" + "=" * 70)
print("FOR BEST RESULTS: ADD PAUSES WITH AUDACITY")
print("=" * 70)

print("\nThe combined file above has NO pauses between affirmations.")
print("For proper meditation pacing, add 4-second pauses:")

print("\n1. Download Audacity (free): https://www.audacityteam.org/")
print("\n2. Open Audacity and import files in this exact order:")
print("   File → Import → Audio")
print("   a. intro.mp3")
print("   b. opening075.mp3")
print("   c. affirmation_01.mp3")
print("   d. affirmation_02.mp3")
print("   e. ... (all affirmations in order)")
print("   f. closing.mp3")

print("\n3. Add 4-second pauses between affirmations:")
print("   • Click at the end of affirmation_01.mp3")
print("   • Generate → Silence → Duration: 4000 milliseconds")
print("   • Repeat for between EACH affirmation")

print("\n4. Export final podcast:")
print("   • File → Export → Export as MP3")
print("   • Name: Ironhack_Mindfulness_Podcast_With_Pauses.mp3")
print("   • Quality: 192 kbps (good quality)")

print("\n" + "=" * 70)
print("ALTERNATIVE: RENAME OPENING FILE")
print("=" * 70)

print("\nIf you want the opening at speed 1.0 (like intro/closing):")
print("cd /Users/carolinanami/Ironhack_Podcast_Project/ironhack_mindfulness_podcast_final")
print("cp opening075.mp3 opening.mp3")
print("\nThen regenerate opening at speed 1.0:")
print("cd src")
print("python -c \"")
print("from dotenv import load_dotenv")
print("from openai import OpenAI")
print("load_dotenv()")
print("client = OpenAI()")
print("with open('../1. Input/Script Opening', 'r') as f:")
print("    text = f.read()")
print("response = client.audio.speech.create(")
print("    model='tts-1', voice='nova', input=text, speed=1.0")
print(")")
print("response.stream_to_file('../ironhack_mindfulness_podcast_final/opening.mp3')")
print("\"")

print("\n" + "=" * 70)
print("🎧 YOUR PODCAST IS READY!")
print("=" * 70)

if os.path.exists(output_file):
    print(f"\n📁 Location: {os.path.abspath(output_file)}")
    print("\nListen to the file to check the flow.")
    print("If you want pauses between affirmations, use Audacity.")
else:
    print(f"\n❌ Combined file not created.")
    print("   Use Audacity to combine manually with pauses.")

print("\n" + "=" * 70)
