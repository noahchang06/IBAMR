#!/usr/bin/env python3
"""Extract a single frame from the GIF to preview."""
from PIL import Image

# Open GIF
gif = Image.open('cardiac_valve_animation.gif')

# Extract frame at peak systole (frame ~45 out of 240)
# This is about 1/8 through the cycle
gif.seek(45)

# Save as static PNG
gif.convert('RGB').save('animation_preview_frame.png')
print("Saved preview frame: animation_preview_frame.png")

# Print GIF info
print(f"\nGIF Information:")
print(f"  Size: {gif.size[0]} x {gif.size[1]} pixels")
print(f"  Frames: {gif.n_frames}")
print(f"  Mode: {gif.mode}")
print(f"  Duration per frame: {gif.info.get('duration', 'N/A')} ms")
