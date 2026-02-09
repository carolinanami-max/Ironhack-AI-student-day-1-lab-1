import os

print("=" * 60)
print("DEBUG: CHECKING TEXT BEING SENT TO TTS")
print("=" * 60)

script_files = {
    "intro": "../1. Input/Script Intro",
    "opening": "../1. Input/Script Opening",
    "meditation": "../1. Input/Script Affirmations",
    "closing": "../1. Input/Script Closing"
}

for name, filepath in script_files.items():
    print(f"\n{name.upper()}:")
    print("-" * 40)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read().strip()
        
        print(f"Total characters: {len(text)}")
        print(f"Total words: {len(text.split())}")
        print(f"First 200 chars: '{text[:200]}'")
        print(f"Last 200 chars: '{text[-200:]}'")
        
        # Check for issues
        if len(text) < 100:
            print("⚠ WARNING: Text seems very short")
        if '...' in text:
            print("⚠ WARNING: Contains '...' which might stop TTS")
        if text.count('.') < 3:
            print("⚠ WARNING: Very few sentences")
            
    except Exception as e:
        print(f"ERROR: {e}")
    
    print("-" * 40)

print("\n" + "=" * 60)
print("Based on 150 words/minute, estimated times:")
print("=" * 60)

for name, filepath in script_files.items():
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read().strip()
    words = len(text.split())
    minutes = words / 150
    print(f"{name}: {words} words = ~{minutes:.1f} minutes")
