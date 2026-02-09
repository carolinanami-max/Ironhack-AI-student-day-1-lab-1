import os
import glob
import subprocess
import sys

print("=" * 70)
print("CREATING FINAL MEDITATION PODCAST")
print("=" * 70)

# Check if ffmpeg is installed
def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

if not check_ffmpeg():
    print("\n❌ ffmpeg is not installed!")
    print("\nPlease install ffmpeg first:")
    print("1. For Mac: brew install ffmpeg")
    print("2. Or download from: https://ffmpeg.org/download.html")
    print("\nAlternatively, use Audacity for manual combining.")
    sys.exit(1)

# Define paths
source_dir = "../ironhack_mindfulness_podcast_final"
output_file = "../ironhack_mindfulness_podcast_final/final_podcast.mp3"

print(f"\nSource directory: {os.path.abspath(source_dir)}")
print(f"Output file: {os.path.abspath(output_file)}")

# List all files in correct order
print("\n" + "=" * 70)
print("FILES TO COMBINE (in order):")
print("=" * 70)

# Get files in correct order
files_in_order = []

# 1. Intro
intro_file = os.path.join(source_dir, "intro.mp3")
if os.path.exists(intro_file):
    files_in_order.append(intro_file)
    print(f"1. intro.mp3")

# 2. Opening
opening_file = os.path.join(source_dir, "opening.mp3")
if os.path.exists(opening_file):
    files_in_order.append(opening_file)
    print(f"2. opening.mp3")

# 3. Affirmations (1-19)
affirmation_files = sorted(glob.glob(os.path.join(source_dir, "affirmation_*.mp3")))
for i, file in enumerate(affirmation_files, 1):
    files_in_order.append(file)
    print(f"{i+2}. {os.path.basename(file)}")

# 4. Closing
closing_file = os.path.join(source_dir, "closing.mp3")
if os.path.exists(closing_file):
    files_in_order.append(closing_file)
    print(f"{len(files_in_order)}. closing.mp3")

print(f"\nTotal files to combine: {len(files_in_order)}")

# Method 1: Simple concatenation (no pauses added)
print("\n" + "=" * 70)
print("METHOD 1: SIMPLE CONCATENATION")
print("=" * 70)
print("\nThis will combine files without adding extra pauses.")
print("Affirmations will flow directly one after another.")

# Create file list for ffmpeg
filelist_path = os.path.join(source_dir, "filelist.txt")
with open(filelist_path, 'w') as f:
    for file in files_in_order:
        f.write(f"file '{os.path.abspath(file)}'\n")

print(f"\nCreated file list: {filelist_path}")

# Combine using ffmpeg
print("\nCombining files...")
try:
    cmd = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", filelist_path,
        "-c", "copy",
        output_file
    ]
    
    print(f"Running: {' '.join(cmd[:5])}... {output_file}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"\n✅ SUCCESS! Created: {output_file}")
            print(f"   Size: {file_size/1000000:.1f} MB")
            
            # Estimate duration (rough)
            duration_seconds = file_size / 16000
            print(f"   Estimated duration: {duration_seconds/60:.1f} minutes")
        else:
            print(f"\n❌ File was not created")
    else:
        print(f"\n❌ ffmpeg error:")
        print(result.stderr)
        
except Exception as e:
    print(f"\n❌ Error: {e}")

# Method 2: With pauses between affirmations
print("\n" + "=" * 70)
print("METHOD 2: WITH PAUSES (Requires Audio Editing)")
print("=" * 70)

print("\nFor proper pauses between affirmations:")
print("1. Open Audacity (free)")
print("2. Import all files in order:")
for i, file in enumerate(files_in_order, 1):
    print(f"   {i}. {os.path.basename(file)}")

print("\n3. Between EACH affirmation, add silence:")
print("   - Click at the end of affirmation_01.mp3")
print("   - Generate → Silence → Duration: 4000 ms (4 seconds)")
print("   - Repeat for each affirmation gap")

print("\n4. Export:")
print("   - File → Export → Export as MP3")
print("   - Name: Ironhack_Mindfulness_Podcast_Final.mp3")

print("\n" + "=" * 70)
print("FINAL INSTRUCTIONS")
print("=" * 70)

print(f"\n📁 Your files are in: {os.path.abspath(source_dir)}")

if os.path.exists(output_file):
    print(f"\n🎧 Simple combined version created:")
    print(f"   {os.path.basename(output_file)}")
    print(f"\n⚠ Note: This version has NO pauses between affirmations.")
    print("   For the best meditation experience, use Audacity to add pauses.")
else:
    print(f"\n❌ Could not create combined file automatically.")
    print("   Please use Audacity to combine manually.")

print("\n" + "=" * 70)
print("PODCAST COMPLETE!")
print("=" * 70)
