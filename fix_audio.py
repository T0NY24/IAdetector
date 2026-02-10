# Fix corrupted audio_forensics.py
import re

with open('modules/audio_forensics.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix line 136 (index 136)
if len(lines) > 136:
    # Remove the corrupted pattern
    lines[136] = '            logger.info(f"   🔍 DEBUG - Probs: {probs[0].tolist()}")\n'
    print(f"Fixed line 137: {lines[136][:50]}...")

with open('modules/audio_forensics.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✅ Audio forensics file fixed!")
