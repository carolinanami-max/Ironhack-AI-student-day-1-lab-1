import os
from tts_generator import TTSGenerator

print("=" * 50)
print("Meditation Podcast Creator")
print("=" * 50)

# Create TTS generator
print("\n1. Creating TTS generator...")
tts = TTSGenerator()

# Meditation parts
parts = {
    "intro": "Welcome to your meditation. Find a comfortable seat.",
    "opening": "Take a deep breath in, and slowly exhale.",
    "meditation": "Feel your body relaxing with each breath.",
    "closing": "Slowly bring your awareness back. Thank you."
}

print(f"\n2. Will create {len(parts)} audio files")

# Create output folder
output_dir = "../output"
os.makedirs(output_dir, exist_ok=True)

# Generate audio
print("\n3. Generating audio...")
for name, text in parts.items():
    filename = f"{output_dir}/{name}.mp3"
    print(f"\n   {name}:")
    tts.generate_speech(text, filename, name)

print("\n" + "=" * 50)
print("✅ Done! Check the 'output' folder.")
print("=" * 50)
