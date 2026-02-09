import os

print("=" * 60)
print("CHECKING MEDITATION SCRIPT FILES")
print("=" * 60)

files = {
    "intro": "../1. Input/Script Intro",
    "opening": "../1. Input/Script Opening", 
    "affirmations": "../1. Input/Script Affirmations",
    "closing": "../1. Input/Script Closing"
}

for name, path in files.items():
    print(f"\n{name.upper()}:")
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                text = f.read()
            print(f"  ✓ Found: {len(text)} chars")
            # Show first line
            first_line = text.split('\n')[0][:80]
            print(f"  Preview: {first_line}...")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    else:
        print(f"  ✗ Not found")

print("\n" + "=" * 60)
