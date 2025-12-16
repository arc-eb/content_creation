"""
Quick run script for iterative prompt testing.
Generates one image at a time and displays it for easy iteration in Cursor.

Usage:
    python run_and_preview.py                          # Uses default: porte1.png + aplat-colmontant.jpg
    python run_and_preview.py --model porte1.png       # Specify model image
    python run_and_preview.py --flatlay aplat_torsade.jpg  # Specify flat-lay image
    python run_and_preview.py --model porte1.png --flatlay aplat_torsade.jpg  # Both
    python run_and_preview.py --luxury                 # Use luxury cashmere prompt
"""
import os
import sys
import argparse
from pathlib import Path

from config import Config
from gemini_client import GeminiGarmentSwapClient
from prompt_generator import PromptGenerator


def display_image_in_cursor(image_path: Path):
    """
    Display image path in a way that Cursor can preview.
    Cursor will automatically show image previews for file paths.
    """
    abs_path = image_path.absolute()
    print(f"\n{'='*60}")
    print(f"📸 IMAGE GENERATED: {image_path.name}")
    print(f"📁 Full path: {abs_path}")
    print(f"{'='*60}")
    print("\n💡 In Cursor:")
    print(f"   - Click on the file path above to preview")
    print(f"   - Or open: {abs_path}")
    print(f"   - File is saved and ready for review")
    print()


def run_single_test(
    model_image: str,
    flatlay_image: str,
    use_custom_prompt: bool = False,
):
    """
    Run a single garment swap for quick iteration.
    
    Args:
        model_image: Model image filename
        flatlay_image: Flat-lay image filename
        use_custom_prompt: If True, uses luxury cashmere prompt template
    """
    # Set API key from old file if not in env (for quick testing)
    if not os.getenv("GEMINI_API_KEY"):
        # Fallback: use the key from the old script (for development only)
        print("ERROR: GEMINI_API_KEY environment variable not set!")
        print("Please set it using: export GEMINI_API_KEY='your-api-key'")
        sys.exit(1)
    
    try:
        # Initialize
        config = Config.from_env()
        config.ensure_directories()
        client = GeminiGarmentSwapClient(config)
        prompt_gen = PromptGenerator()
        
        # Resolve input paths (support legacy structure)
        model_path = config.input_models_dir / model_image
        flatlay_path = config.input_aplat_dir / flatlay_image
        
        # If files not found, try legacy location
        if not model_path.exists():
            legacy_model = config.base_dir / "test_nanobanana" / "input" / model_image
            if legacy_model.exists():
                model_path = legacy_model
            else:
                raise FileNotFoundError(f"Model image not found: {model_image}")
        
        if not flatlay_path.exists():
            legacy_flatlay = config.base_dir / "test_nanobanana" / "input" / flatlay_image
            if legacy_flatlay.exists():
                flatlay_path = legacy_flatlay
            else:
                raise FileNotFoundError(f"Flat-lay image not found: {flatlay_image}")
        
        # Generate prompt
        if use_custom_prompt:
            prompt = prompt_gen.generate_luxury_cashmere_prompt(
                color="beige",
                style="turtleneck",
                knit_pattern="cable knit",
            )
            print("📝 Using luxury cashmere prompt template")
        else:
            prompt = prompt_gen.generate_garment_swap_prompt()
            print("📝 Using default prompt")
        
        # Generate output path
        output_path = config.get_output_path(model_image, flatlay_image)
        
        print(f"\n🎨 Processing: {model_image} + {flatlay_image}")
        print(f"⏳ Calling Gemini API... (this may take 30-60 seconds)")
        
        # Perform swap
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
            
            # Display for Cursor
            display_image_in_cursor(result_path)
            return result_path
        else:
            print("❌ Failed to generate image")
            return None
            
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Bompard Content Creation - Quick Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_and_preview.py
  python run_and_preview.py --model porte1.png --flatlay aplat_torsade.jpg
  python run_and_preview.py --flatlay aplat-colmontant.jpg --luxury
        """
    )
    
    parser.add_argument(
        "--model",
        type=str,
        default="porte1.png",
        help="Model/pose image filename (default: porte1.png)"
    )
    
    parser.add_argument(
        "--flatlay",
        type=str,
        default="aplat-colmontant.jpg",
        help="Flat-lay product image filename (default: aplat-colmontant.jpg)"
    )
    
    parser.add_argument(
        "--luxury",
        action="store_true",
        help="Use luxury cashmere prompt template instead of default"
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("Bompard Content Creation - Quick Test Runner")
    print("="*60)
    print()
    
    print(f"Configuration:")
    print(f"  Model: {args.model}")
    print(f"  Flat-lay: {args.flatlay}")
    print(f"  Prompt: {'Luxury cashmere template' if args.luxury else 'Default'}")
    print()
    
    result = run_single_test(
        model_image=args.model,
        flatlay_image=args.flatlay,
        use_custom_prompt=args.luxury,
    )
    
    if result:
        print("\n✨ Success! Check the image above.")
        print("\n💡 To iterate:")
        print("   1. Review the generated image")
        print("   2. Modify the prompt in prompt_generator.py")
        print("   3. Run this script again with different options")
        print("\n💡 Quick command examples:")
        print(f"   python run_and_preview.py --model {args.model} --flatlay {args.flatlay}")
        print("   python run_and_preview.py --luxury  # Use luxury prompt")
    else:
        print("\n⚠️  Generation failed. Check error messages above.")

