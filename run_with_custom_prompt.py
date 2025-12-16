"""Test script that allows you to easily test custom prompts."""
import os
import sys
from pathlib import Path

from config import Config
from gemini_client import GeminiGarmentSwapClient

# Set API key if needed
if not os.getenv("GEMINI_API_KEY"):
    print("ERROR: GEMINI_API_KEY environment variable not set!")
    print("Please set it using: export GEMINI_API_KEY='your-api-key'")
    sys.exit(1)

# Custom prompt - ultra-explicit structure with clear DO NOT CHANGE vs ONLY CHANGE sections
CUSTOM_PROMPT = """TASK: You have two images - (1) a photo of a model, (2) a flat-lay photo of a garment.
Replace ONLY the clothing on the model with the garment from the flat-lay image.
Everything else in the image must remain identical.

PRESERVE (keep identical):
DO NOT CHANGE: The model's face - keep it identical (same features, expression, skin tone, hair, makeup).
DO NOT CHANGE: The model's pose, body, proportions, posture, position, or stance.
DO NOT CHANGE: The lighting - keep it identical (same direction, intensity, shadows, highlights).
DO NOT CHANGE: The background - keep it identical.

REPLACE (change this only):
ONLY CHANGE: The garment. Replace the model's current clothing with the garment from the flat-lay image.
Use the garment exactly as shown in the flat-lay - same color, same texture, same patterns, same knit structure, same buttons/details.
The garment should fit the model's body naturally, but its appearance must match the flat-lay image exactly.

Output: Professional fashion photography quality, sharp focus."""

def main():
    if len(sys.argv) < 3:
        print("Usage: python run_with_custom_prompt.py <model_image> <flatlay_image>")
        print("Example: python run_with_custom_prompt.py porte1.png aplat_torsade.jpg")
        sys.exit(1)
    
    model_image = sys.argv[1]
    flatlay_image = sys.argv[2]
    
    print("="*70)
    print("Testing with custom prompt")
    print("="*70)
    print(f"\nModel: {model_image}")
    print(f"Flat-lay: {flatlay_image}")
    print(f"\nPrompt being used:")
    print("-"*70)
    print(CUSTOM_PROMPT)
    print("-"*70)
    print()
    
    config = Config.from_env()
    config.ensure_directories()
    client = GeminiGarmentSwapClient(config)
    
    # Resolve paths
    model_path = config.input_models_dir / model_image
    flatlay_path = config.input_aplat_dir / flatlay_image
    
    if not model_path.exists():
        legacy_model = config.base_dir / "test_nanobanana" / "input" / model_image
        if legacy_model.exists():
            model_path = legacy_model
        else:
            print(f"❌ Model image not found: {model_image}")
            sys.exit(1)
    
    if not flatlay_path.exists():
        legacy_flatlay = config.base_dir / "test_nanobanana" / "input" / flatlay_image
        if legacy_flatlay.exists():
            flatlay_path = legacy_flatlay
        else:
            print(f"❌ Flat-lay image not found: {flatlay_image}")
            sys.exit(1)
    
    output_path = config.get_output_path(model_image, flatlay_image)
    
    print(f"⏳ Calling Gemini API... (this may take 30-60 seconds)\n")
    
    try:
        result_path = client.swap_garment(
            model_image_path=model_path,
            flatlay_image_path=flatlay_path,
            prompt=CUSTOM_PROMPT,
            output_path=output_path,
        )
        
        if result_path and result_path.exists():
            is_valid, message = client.validate_image_quality(result_path)
            print(f"✅ Quality check: {message}")
            print(f"\n{'='*70}")
            print(f"📸 IMAGE GENERATED")
            print(f"{'='*70}")
            print(f"📁 {result_path.absolute()}")
            print(f"{'='*70}\n")
        else:
            print("❌ Failed to generate image")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

