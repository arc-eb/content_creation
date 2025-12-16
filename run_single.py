"""
Simple script to generate a single garment swap.
Pass model and flat-lay filenames as arguments.

Usage:
    python run_single.py porte1.png aplat-colmontant.jpg
    python run_single.py porte1.png aplat_torsade.jpg
"""
import os
import sys
from pathlib import Path

from config import Config
from gemini_client import GeminiGarmentSwapClient
from prompt_generator import PromptGenerator


def main():
    # Set API key if needed
    if not os.getenv("GEMINI_API_KEY"):
        os.environ["GEMINI_API_KEY"] = "AIzaSyC935QLsFzfPgjYr--c3Z7X05n0EOENG0k"
        print("⚠️  Using API key from code (set GEMINI_API_KEY env var for production)")
    
    # Parse arguments
    if len(sys.argv) < 3:
        print("Usage: python run_single.py <model_image> <flatlay_image>")
        print("\nExamples:")
        print("  python run_single.py porte1.png aplat-colmontant.jpg")
        print("  python run_single.py porte1.png aplat_torsade.jpg")
        sys.exit(1)
    
    model_image = sys.argv[1]
    flatlay_image = sys.argv[2]
    
    print("="*60)
    print("Bompard Content Creation - Single Image Generator")
    print("="*60)
    print(f"\nModel: {model_image}")
    print(f"Flat-lay: {flatlay_image}\n")
    
    # Initialize
    config = Config.from_env()
    config.ensure_directories()
    client = GeminiGarmentSwapClient(config)
    prompt_gen = PromptGenerator()
    
    # Generate prompt
    prompt = prompt_gen.generate_garment_swap_prompt()
    
    # Resolve input paths (support legacy structure)
    model_path = config.input_models_dir / model_image
    flatlay_path = config.input_aplat_dir / flatlay_image
    
    # If files not found, try legacy location
    if not model_path.exists():
        legacy_model = config.base_dir / "test_nanobanana" / "input" / model_image
        if legacy_model.exists():
            model_path = legacy_model
        else:
            print(f"❌ Error: Model image not found: {model_image}")
            print(f"   Tried: {model_path}")
            print(f"   Tried: {legacy_model}")
            sys.exit(1)
    
    if not flatlay_path.exists():
        legacy_flatlay = config.base_dir / "test_nanobanana" / "input" / flatlay_image
        if legacy_flatlay.exists():
            flatlay_path = legacy_flatlay
        else:
            print(f"❌ Error: Flat-lay image not found: {flatlay_image}")
            print(f"   Tried: {flatlay_path}")
            print(f"   Tried: {legacy_flatlay}")
            sys.exit(1)
    
    # Generate output path
    output_path = config.get_output_path(model_image, flatlay_image)
    
    print(f"⏳ Calling Gemini API... (this may take 30-60 seconds)\n")
    
    # Perform swap
    try:
        result_path = client.swap_garment(
            model_image_path=model_path,
            flatlay_image_path=flatlay_path,
            prompt=prompt,
            output_path=output_path,
        )
        
        if result_path and result_path.exists():
            # Validate quality
            is_valid, message = client.validate_image_quality(result_path)
            print(f"✅ Quality check: {message}")
            
            print(f"\n{'='*60}")
            print(f"📸 IMAGE GENERATED SUCCESSFULLY")
            print(f"{'='*60}")
            print(f"📁 File: {result_path.name}")
            print(f"📂 Path: {result_path.absolute()}")
            print(f"\n💡 In Cursor: Click on the file path above or open the file in Explorer")
            print(f"{'='*60}\n")
            return result_path
        else:
            print("❌ Failed to generate image")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

