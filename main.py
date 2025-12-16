"""
Main execution script for Bompard luxury content creation tool.
Orchestrates garment swapping workflow with production-grade error handling.
"""
import logging
import sys
from pathlib import Path
from typing import List, Optional

from config import Config
from gemini_client import GeminiGarmentSwapClient
from prompt_generator import PromptGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class GarmentSwapProcessor:
    """Main processor for batch garment swapping operations."""
    
    def __init__(self, config: Config):
        """
        Initialize the processor.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.config.ensure_directories()
        self.client = GeminiGarmentSwapClient(config)
        self.prompt_generator = PromptGenerator()
        logger.info("Initialized GarmentSwapProcessor")
    
    def process_single_swap(
        self,
        model_image: str,
        flatlay_image: str,
        output_filename: Optional[str] = None,
        custom_prompt: Optional[str] = None,
    ) -> Optional[Path]:
        """
        Process a single garment swap operation.
        
        Args:
            model_image: Filename of the model image (in input/models/)
            flatlay_image: Filename of the flat-lay image (in input/aplat/)
            output_filename: Optional custom output filename
            custom_prompt: Optional custom prompt (uses default if not provided)
            
        Returns:
            Path to generated image if successful, None otherwise
        """
        # Resolve input paths
        model_path = self.config.input_models_dir / model_image
        flatlay_path = self.config.input_aplat_dir / flatlay_image
        
        # Generate output path
        if output_filename:
            output_path = self.config.output_dir / output_filename
        else:
            output_path = self.config.get_output_path(model_image, flatlay_image)
        
        # Generate or use custom prompt
        if custom_prompt:
            prompt = custom_prompt
        else:
            prompt = self.prompt_generator.generate_garment_swap_prompt()
        
        logger.info(f"Processing: {model_image} + {flatlay_image} -> {output_path.name}")
        
        # Perform the swap
        try:
            result_path = self.client.swap_garment(
                model_image_path=model_path,
                flatlay_image_path=flatlay_path,
                prompt=prompt,
                output_path=output_path,
            )
            
            if result_path:
                # Validate output quality
                is_valid, message = self.client.validate_image_quality(result_path)
                logger.info(f"Quality check: {message}")
                if not is_valid:
                    logger.warning(f"Quality validation failed: {message}")
                
                return result_path
            else:
                logger.error("Swap operation returned no result")
                return None
                
        except Exception as e:
            logger.error(f"Error processing swap: {e}", exc_info=True)
            return None
    
    def process_batch(
        self,
        model_images: List[str],
        flatlay_image: str,
        custom_prompt: Optional[str] = None,
    ) -> List[Path]:
        """
        Process multiple model images with the same flat-lay garment.
        
        Args:
            model_images: List of model image filenames
            flatlay_image: Filename of the flat-lay image
            custom_prompt: Optional custom prompt
            
        Returns:
            List of paths to successfully generated images
        """
        results = []
        
        logger.info(f"Starting batch processing: {len(model_images)} models × 1 flat-lay")
        
        for i, model_image in enumerate(model_images, 1):
            logger.info(f"\n--- Processing {i}/{len(model_images)}: {model_image} ---")
            
            result = self.process_single_swap(
                model_image=model_image,
                flatlay_image=flatlay_image,
                custom_prompt=custom_prompt,
            )
            
            if result:
                results.append(result)
            else:
                logger.warning(f"Failed to process {model_image}")
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Batch processing complete: {len(results)}/{len(model_images)} successful")
        logger.info(f"{'='*60}")
        
        return results


def main():
    """Main entry point for the script."""
    try:
        # Initialize configuration
        # You can override base_dir by passing a path, or use current directory
        config = Config.from_env()
        
        # Initialize processor
        processor = GarmentSwapProcessor(config)
        
        # ============================================================
        # CONFIGURATION: Update these to match your input files
        # ============================================================
        # Model images should be in: input/models/ (or test_nanobanana/input/ for legacy)
        model_images = [
            "porte1.png",
            "porte2.png",
            "porte3.png",
        ]
        
        # Flat-lay image should be in: input/aplat/ (or test_nanobanana/input/ for legacy)
        flatlay_image = "aplat-colmontant.jpg"
        # ============================================================
        
        # Option 1: Use default prompt (recommended for most cases)
        results = processor.process_batch(
            model_images=model_images,
            flatlay_image=flatlay_image,
        )
        
        # Option 2: Use custom prompt (for specific garment details)
        # from prompt_generator import PromptGenerator
        # custom_prompt = PromptGenerator.generate_luxury_cashmere_prompt(
        #     color="beige",
        #     style="turtleneck",
        #     knit_pattern="cable knit",
        # )
        # results = processor.process_batch(
        #     model_images=model_images,
        #     flatlay_image=flatlay_image,
        #     custom_prompt=custom_prompt,
        # )
        
        # Option 3: Process a single swap
        # result = processor.process_single_swap(
        #     model_image="porte1.png",
        #     flatlay_image="aplat-colmontant.jpg",
        # )
        
        if results:
            print("\n" + "="*60)
            print("✅ SUCCESSFULLY GENERATED IMAGES")
            print("="*60)
            for i, result in enumerate(results, 1):
                abs_path = result.absolute()
                print(f"\n{i}. {result.name}")
                print(f"   📁 {abs_path}")
                print(f"   💡 Click the path above to preview in Cursor")
            print("\n" + "="*60)
        else:
            print("\n❌ No images were generated. Check logs for errors.")
            sys.exit(1)
            
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"\n❌ Configuration error: {e}")
        print("\nPlease set your API key:")
        print("  export GEMINI_API_KEY='your-api-key-here'")
        sys.exit(1)
        
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        print("\n⚠️  Process interrupted by user")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

