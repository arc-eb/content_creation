"""Test with the original prompt style to see if it works better."""
import os
from pathlib import Path

# Use the exact original prompt format
ORIGINAL_STYLE_PROMPT = """Professional fashion photography of a model wearing the exact garment shown in the flat-lay image.
The garment features all the textures, colors, patterns, knit details, and material characteristics visible in the flat-lay.
GARMENT DETAILS: Match the exact garment from the flat-lay image - replicate all textures, colors, patterns, knit structures, and material characteristics with photographic accuracy.
POSE: Keep the model's pose, body proportions, and posture exactly as in the original image.
LIGHTING: Keep the exact same studio lighting setup - direction, intensity, shadows, and highlights as in the original model image.
BACKGROUND: Keep the background exactly as in the original model image.
Camera: Professional fashion editorial style, sharp focus throughout, especially on garment texture details.
keep the exact same model face."""

print("="*70)
print("ORIGINAL STYLE PROMPT (describes output, not instructions):")
print("="*70)
print(ORIGINAL_STYLE_PROMPT)
print("="*70)

