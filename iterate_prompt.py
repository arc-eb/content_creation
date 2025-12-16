"""
Interactive script for iterating on prompts.
Shows the current prompt and makes it easy to test variations.
"""
import os
import sys
from pathlib import Path

from config import Config
from gemini_client import GeminiGarmentSwapClient
from prompt_generator import PromptGenerator


def show_current_prompt(prompt_type="default"):
    """Display the current prompt being used."""
    prompt_gen = PromptGenerator()
    
    if prompt_type == "luxury":
        prompt = prompt_gen.generate_luxury_cashmere_prompt(
            color="beige",
            style="turtleneck",
            knit_pattern="cable knit",
        )
        print("="*70)
        print("CURRENT PROMPT (Luxury Cashmere Template):")
        print("="*70)
    else:
        prompt = prompt_gen.generate_garment_swap_prompt()
        print("="*70)
        print("CURRENT PROMPT (Default):")
        print("="*70)
    
    print(prompt)
    print("="*70)
    return prompt


def quick_test(model="porte1.png", flatlay="aplat-colmontant.jpg", prompt_type="default", custom_prompt=None, show_prompt=True):
    """
    Quick test with current prompt.
    
    Args:
        model: Model image filename
        flatlay: Flat-lay image filename  
        prompt_type: "default" or "luxury"
        custom_prompt: Optional custom prompt string to override
    """
    # Set API key if needed
    if not os.getenv("GEMINI_API_KEY"):
        print("ERROR: GEMINI_API_KEY environment variable not set!")
        print("Please set it using: export GEMINI_API_KEY='your-api-key'")
        sys.exit(1)
    
    config = Config.from_env()
    config.ensure_directories()
    client = GeminiGarmentSwapClient(config)
    prompt_gen = PromptGenerator()
    
    # Get prompt
    if custom_prompt:
        prompt = custom_prompt
        print("📝 Using CUSTOM prompt")
    elif prompt_type == "luxury":
        prompt = prompt_gen.generate_luxury_cashmere_prompt(
            color="beige",
            style="turtleneck",
            knit_pattern="cable knit",
        )
        print("📝 Using luxury cashmere prompt template")
    else:
        prompt = prompt_gen.generate_garment_swap_prompt()
        print("📝 Using default prompt")
    
    # Show prompt
    if show_prompt:
        print("\n" + "="*70)
        print("PROMPT TO USE:")
        print("="*70)
        print(prompt)
        print("="*70 + "\n")
    
    # Resolve paths
    model_path = config.input_models_dir / model
    flatlay_path = config.input_aplat_dir / flatlay
    
    if not model_path.exists():
        legacy_model = config.base_dir / "test_nanobanana" / "input" / model
        if legacy_model.exists():
            model_path = legacy_model
        else:
            raise FileNotFoundError(f"Model image not found: {model}")
    
    if not flatlay_path.exists():
        legacy_flatlay = config.base_dir / "test_nanobanana" / "input" / flatlay
        if legacy_flatlay.exists():
            flatlay_path = legacy_flatlay
        else:
            raise FileNotFoundError(f"Flat-lay image not found: {flatlay}")
    
    output_path = config.get_output_path(model, flatlay)
    
    print(f"🎨 Processing: {model} + {flatlay}")
    print(f"💾 Output will be saved to: {output_path}")
    print(f"⏳ Calling Gemini API... (this may take 30-60 seconds)\n")
    
    result_path = client.swap_garment(
        model_image_path=model_path,
        flatlay_image_path=flatlay_path,
        prompt=prompt,
        output_path=output_path,
    )
    
    if result_path and result_path.exists():
        is_valid, message = client.validate_image_quality(result_path)
        print(f"\n✅ Quality check: {message}")
        print(f"\n{'='*70}")
        print(f"📸 IMAGE GENERATED SUCCESSFULLY")
        print(f"{'='*70}")
        print(f"📁 File: {result_path.name}")
        print(f"📂 Path: {result_path.absolute()}")
        print(f"\n💡 In Cursor: Click on the file path above or open:")
        print(f"   {result_path.absolute()}")
        print(f"{'='*70}\n")
        return result_path
    else:
        print("❌ Failed to generate image")
        return None


if __name__ == "__main__":
    print("\n" + "="*70)
    print("PROMPT ITERATION TOOL")
    print("="*70)
    print("\nThis script helps you test and iterate on prompts.")
    print("\nOptions:")
    print("  1. Show current default prompt")
    print("  2. Show current luxury cashmere prompt")
    print("  3. Run quick test with default prompt")
    print("  4. Run quick test with luxury prompt")
    print("\nTo modify prompts, edit: prompt_generator.py")
    print("="*70 + "\n")
    
    # Default: run quick test
    import sys
    if len(sys.argv) > 1:
        action = sys.argv[1]
        if action == "show-default":
            show_current_prompt("default")
        elif action == "show-luxury":
            show_current_prompt("luxury")
        elif action == "test-default":
            quick_test(prompt_type="default")
        elif action == "test-luxury":
            quick_test(prompt_type="luxury")
        else:
            print(f"Unknown action: {action}")
            print("Usage: python iterate_prompt.py [show-default|show-luxury|test-default|test-luxury]")
    else:
        # Default: run test with default prompt
        print("Running quick test with default prompt...\n")
        quick_test(prompt_type="default")

