"""
Interactive prompt iteration tool.
Run a swap, review the result, then add refinement instructions to improve it.
"""
import os
import sys
from pathlib import Path

from config import Config
from gemini_client import GeminiGarmentSwapClient
from prompt_generator import PromptGenerator


def load_base_prompt():
    """Load the base prompt from the prompt generator."""
    prompt_gen = PromptGenerator()
    return prompt_gen.generate_garment_swap_prompt()


def load_refinement_notes():
    """Load any existing refinement notes from a file."""
    notes_file = Path("prompt_refinement.txt")
    if notes_file.exists():
        with open(notes_file, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""


def save_refinement_notes(notes: str):
    """Save refinement notes to a file."""
    notes_file = Path("prompt_refinement.txt")
    with open(notes_file, "w", encoding="utf-8") as f:
        f.write(notes)


def build_prompt_with_refinements(base_prompt: str, refinements: str) -> str:
    """Combine base prompt with refinement instructions."""
    if not refinements or not refinements.strip():
        return base_prompt
    
    # Add refinements as additional instructions
    refined_prompt = base_prompt
    refined_prompt += "\n\n"
    refined_prompt += "ADDITIONAL REFINEMENTS (based on previous iteration):"
    refined_prompt += "\n"
    refined_prompt += refinements
    
    return refined_prompt


def run_swap(
    model_image: str,
    flatlay_image: str,
    prompt: str,
    output_suffix: str = ""
):
    """Run a single garment swap."""
    # Set API key if needed
    if not os.getenv("GEMINI_API_KEY"):
        os.environ["GEMINI_API_KEY"] = "AIzaSyC935QLsFzfPgjYr--c3Z7X05n0EOENG0k"
    
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
            raise FileNotFoundError(f"Model image not found: {model_image}")
    
    if not flatlay_path.exists():
        legacy_flatlay = config.base_dir / "test_nanobanana" / "input" / flatlay_image
        if legacy_flatlay.exists():
            flatlay_path = legacy_flatlay
        else:
            raise FileNotFoundError(f"Flat-lay image not found: {flatlay_image}")
    
    # Generate output path with suffix for iterations
    base_output_name = config.get_output_path(model_image, flatlay_image)
    if output_suffix:
        stem = base_output_name.stem
        output_path = base_output_name.parent / f"{stem}_{output_suffix}{base_output_name.suffix}"
    else:
        output_path = base_output_name
    
    print(f"\n⏳ Calling Gemini API... (this may take 30-60 seconds)\n")
    
    try:
        result_path = client.swap_garment(
            model_image_path=model_path,
            flatlay_image_path=flatlay_path,
            prompt=prompt,
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
            return result_path
        else:
            print("❌ Failed to generate image")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    print("="*70)
    print("GARMENT SWAP - PROMPT ITERATION TOOL")
    print("="*70)
    print("\nThis tool lets you iterate on prompts to improve results.")
    print("After each generation, you can add refinement instructions.\n")
    
    # Get inputs
    if len(sys.argv) >= 3:
        model_image = sys.argv[1]
        flatlay_image = sys.argv[2]
    else:
        model_image = input("Model image filename (e.g., porte1.png): ").strip()
        flatlay_image = input("Flat-lay image filename (e.g., aplat_rose.png): ").strip()
    
    # Load base prompt and refinements
    base_prompt = load_base_prompt()
    refinements = load_refinement_notes()
    
    iteration = 1
    
    while True:
        print("\n" + "="*70)
        print(f"ITERATION {iteration}")
        print("="*70)
        
        # Build prompt
        if refinements:
            print("\n📝 Current refinement notes:")
            print("-" * 70)
            print(refinements)
            print("-" * 70)
            full_prompt = build_prompt_with_refinements(base_prompt, refinements)
        else:
            print("\n📝 Using base prompt (no refinements yet)")
            full_prompt = base_prompt
        
        # Show prompt preview
        show_prompt = input("\nShow full prompt? (y/n, default n): ").strip().lower()
        if show_prompt == 'y':
            print("\n" + "="*70)
            print("FULL PROMPT:")
            print("="*70)
            print(full_prompt)
            print("="*70)
        
        # Run swap
        output_suffix = f"iter{iteration}" if iteration > 1 else ""
        result_path = run_swap(
            model_image=model_image,
            flatlay_image=flatlay_image,
            prompt=full_prompt,
            output_suffix=output_suffix
        )
        
        if not result_path:
            print("\n❌ Generation failed. Exiting.")
            break
        
        # Ask for refinements
        print("\n" + "="*70)
        print("REVIEW THE IMAGE")
        print("="*70)
        print(f"Check the result: {result_path.absolute()}")
        print("\nWhat needs to be improved? (Enter refinement instructions)")
        print("Examples:")
        print("  - 'Make the garment color match the flat-lay more precisely'")
        print("  - 'Keep the model's expression exactly as original'")
        print("  - 'Preserve the exact texture from the flat-lay'")
        print("  - 'Do not modify the lighting at all'")
        print("\n(Leave empty to exit, or 'reset' to clear all refinements)")
        
        new_refinements = input("\nRefinement instructions: ").strip()
        
        if not new_refinements:
            print("\n✅ Finished iterating. Final image saved.")
            break
        elif new_refinements.lower() == 'reset':
            refinements = ""
            save_refinement_notes("")
            print("\n🔄 Refinements cleared. Starting fresh.")
            iteration = 1
            continue
        else:
            # Append or replace refinements
            if refinements:
                refinements += "\n" + new_refinements
            else:
                refinements = new_refinements
            save_refinement_notes(refinements)
            print(f"\n💾 Refinements saved. Will be applied to next iteration.")
            iteration += 1


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user. Exiting.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

