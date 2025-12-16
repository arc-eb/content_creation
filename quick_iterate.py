"""
Quick iteration script - edit prompt_refinement.txt and run again.
"""
import os
import sys
from pathlib import Path

from config import Config
from gemini_client import GeminiGarmentSwapClient
from prompt_generator import PromptGenerator


def main():
    if len(sys.argv) < 3:
        print("Usage: python quick_iterate.py <model_image> <flatlay_image>")
        print("\nExample: python quick_iterate.py porte1.png aplat_rose.png")
        print("\nTo refine the prompt:")
        print("  1. Edit prompt_refinement.txt and add your refinement instructions")
        print("  2. Run this script again")
        print("  3. Review the output and repeat")
        sys.exit(1)
    
    model_image = sys.argv[1]
    flatlay_image = sys.argv[2]
    
    # API key must be set via environment variable
    if not os.getenv("GEMINI_API_KEY"):
        print("ERROR: GEMINI_API_KEY environment variable not set!")
        print("Please set it using: export GEMINI_API_KEY='your-api-key'")
        sys.exit(1)
    
    # Load base prompt
    prompt_gen = PromptGenerator()
    base_prompt = prompt_gen.generate_garment_swap_prompt()
    
    # Load refinements
    refinements_file = Path("prompt_refinement.txt")
    refinements = ""
    if refinements_file.exists():
        with open(refinements_file, "r", encoding="utf-8") as f:
            refinements = f.read().strip()
    
    # Build full prompt
    if refinements:
        full_prompt = base_prompt
        full_prompt += "\n\n"
        full_prompt += "ADDITIONAL REFINEMENTS (based on previous iteration):"
        full_prompt += "\n"
        full_prompt += refinements
        print("📝 Using prompt with refinements from prompt_refinement.txt")
    else:
        full_prompt = base_prompt
        print("📝 Using base prompt (no refinements)")
        print("💡 Tip: Create prompt_refinement.txt to add refinement instructions")
    
    # Show prompt if requested
    if "--show-prompt" in sys.argv:
        print("\n" + "="*70)
        print("FULL PROMPT:")
        print("="*70)
        print(full_prompt)
        print("="*70 + "\n")
    
    # Initialize
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
    
    print(f"\n🎨 Processing: {model_image} + {flatlay_image}")
    print(f"⏳ Calling Gemini API... (this may take 30-60 seconds)\n")
    
    try:
        result_path = client.swap_garment(
            model_image_path=model_path,
            flatlay_image_path=flatlay_path,
            prompt=full_prompt,
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
            print("💡 To iterate:")
            print("  1. Review the image above")
            print("  2. Edit prompt_refinement.txt with your refinement instructions")
            print("  3. Run this script again")
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

