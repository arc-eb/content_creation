"""
Simple example usage of the Bompard content creation tool.
This demonstrates basic usage patterns.
"""
import os
from pathlib import Path

from config import Config
from gemini_client import GeminiGarmentSwapClient
from prompt_generator import PromptGenerator
from main import GarmentSwapProcessor


def example_basic_usage():
    """Basic example: process one model with one flat-lay."""
    # Initialize (requires GEMINI_API_KEY environment variable)
    config = Config.from_env()
    processor = GarmentSwapProcessor(config)
    
    # Process single swap
    result = processor.process_single_swap(
        model_image="porte1.png",
        flatlay_image="aplat-colmontant.jpg",
    )
    
    if result:
        print(f"✅ Generated image: {result}")
    else:
        print("❌ Failed to generate image")


def example_batch_processing():
    """Example: process multiple models with one flat-lay."""
    config = Config.from_env()
    processor = GarmentSwapProcessor(config)
    
    model_images = ["porte1.png", "porte2.png", "porte3.png"]
    flatlay_image = "aplat-colmontant.jpg"
    
    results = processor.process_batch(
        model_images=model_images,
        flatlay_image=flatlay_image,
    )
    
    print(f"✅ Generated {len(results)} images")


def example_custom_prompt():
    """Example: use a custom prompt for specific garment details."""
    config = Config.from_env()
    processor = GarmentSwapProcessor(config)
    
    # Generate luxury cashmere prompt with specific details
    prompt_gen = PromptGenerator()
    custom_prompt = prompt_gen.generate_luxury_cashmere_prompt(
        color="beige",
        style="turtleneck",
        knit_pattern="cable knit",
    )
    
    result = processor.process_single_swap(
        model_image="porte1.png",
        flatlay_image="aplat-colmontant.jpg",
        custom_prompt=custom_prompt,
    )
    
    if result:
        print(f"✅ Generated image with custom prompt: {result}")


def example_fully_custom_prompt():
    """Example: create a completely custom prompt."""
    config = Config.from_env()
    processor = GarmentSwapProcessor(config)
    
    # Your custom prompt
    my_prompt = """
    Replace the garment on the model with the exact cashmere sweater from the flat-lay image.
    Preserve the model's face, lighting, and background exactly as they appear.
    Focus on capturing the intricate cable knit texture with maximum detail.
    The sweater should fit naturally and look photorealistic.
    """
    
    result = processor.process_single_swap(
        model_image="porte1.png",
        flatlay_image="aplat-colmontant.jpg",
        custom_prompt=my_prompt,
    )
    
    if result:
        print(f"✅ Generated image with fully custom prompt: {result}")


if __name__ == "__main__":
    # Uncomment the example you want to run:
    
    # example_basic_usage()
    # example_batch_processing()
    # example_custom_prompt()
    # example_fully_custom_prompt()
    
    print("Please uncomment one of the example functions to run it.")
    print("Make sure GEMINI_API_KEY environment variable is set!")

