"""
Gemini API client for garment swapping operations.
Handles API communication, error handling, and retries.
"""
import time
import logging
from pathlib import Path
from typing import Optional, Tuple
from io import BytesIO

from google import genai
from google.genai.errors import APIError
from PIL import Image

from config import Config

logger = logging.getLogger(__name__)


class GeminiGarmentSwapClient:
    """Client for performing garment swaps using Gemini 2.5 Flash Image model."""
    
    def __init__(self, config: Config):
        """
        Initialize the Gemini client.
        
        Args:
            config: Configuration object with API key and settings
        """
        self.config = config
        self.client = genai.Client(api_key=config.api_key)
        logger.info(f"Initialized Gemini client with model: {config.model_name}")
    
    def swap_garment(
        self,
        model_image_path: Path,
        flatlay_image_path: Path,
        prompt: str,
        output_path: Path,
        max_output_size: Optional[int] = None,
        additional_image_path: Optional[Path] = None,
    ) -> Optional[Path]:
        """
        Perform a garment swap using Gemini API.
        
        Args:
            model_image_path: Path to the model/pose image
            flatlay_image_path: Path to the flat-lay product image
            prompt: The prompt describing the desired result
            output_path: Path where the output image should be saved
            max_output_size: Optional maximum dimension for output image (resizes if larger)
            additional_image_path: Optional path to an additional image for guidance
            
        Returns:
            Path to the saved output image if successful, None otherwise
        """
        # Validate input files exist
        if not model_image_path.exists():
            logger.error(f"Model image not found: {model_image_path}")
            raise FileNotFoundError(f"Model image not found: {model_image_path}")
        
        if not flatlay_image_path.exists():
            logger.error(f"Flat-lay image not found: {flatlay_image_path}")
            raise FileNotFoundError(f"Flat-lay image not found: {flatlay_image_path}")
        
        if additional_image_path and not additional_image_path.exists():
            logger.error(f"Additional image not found: {additional_image_path}")
            raise FileNotFoundError(f"Additional image not found: {additional_image_path}")
        
        log_msg = f"Processing garment swap: {model_image_path.name} + {flatlay_image_path.name}"
        if additional_image_path:
            log_msg += f" + additional: {additional_image_path.name}"
        logger.info(log_msg)
        
        # Retry logic
        last_exception = None
        for attempt in range(1, self.config.max_retries + 1):
            try:
                result = self._perform_swap(
                    model_image_path, flatlay_image_path, prompt, output_path, max_output_size, additional_image_path
                )
                if result:
                    logger.info(f"✅ Successfully saved image to: {output_path}")
                    return result
                    
            except APIError as e:
                last_exception = e
                logger.warning(
                    f"API error on attempt {attempt}/{self.config.max_retries}: {e}"
                )
                if attempt < self.config.max_retries:
                    time.sleep(self.config.retry_delay * attempt)  # Exponential backoff
                    continue
                else:
                    logger.error(f"Failed after {self.config.max_retries} attempts")
                    raise
                    
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                raise
        
        return None
    
    def _perform_swap(
        self,
        model_image_path: Path,
        flatlay_image_path: Path,
        prompt: str,
        output_path: Path,
        max_output_size: Optional[int] = None,
        additional_image_path: Optional[Path] = None,
    ) -> Optional[Path]:
        """Internal method to perform the actual API call."""
        # Load images
        try:
            model_image = Image.open(model_image_path)
            flatlay_image = Image.open(flatlay_image_path)
            additional_image = None
            if additional_image_path:
                additional_image = Image.open(additional_image_path)
                logger.info(
                    f"Additional image: {additional_image.size}, mode: {additional_image.mode}, "
                    f"format: {additional_image.format}"
                )
        except Exception as e:
            logger.error(f"Error loading images: {e}")
            raise
        
        # Log image info for debugging
        logger.info(
            f"Model image: {model_image.size}, mode: {model_image.mode}, "
            f"format: {model_image.format}"
        )
        logger.info(
            f"Flat-lay image: {flatlay_image.size}, mode: {flatlay_image.mode}, "
            f"format: {flatlay_image.format}"
        )
        
        # Check image sizes and potentially resize if too large
        # Use smaller max dimension when additional image is present (3 images total)
        max_dimension = 1536 if additional_image else 2048
        
        model_max = max(model_image.size)
        flatlay_max = max(flatlay_image.size)
        additional_max = max(additional_image.size) if additional_image else 0
        
        # Always resize if any image exceeds max_dimension
        if model_max > max_dimension or flatlay_max > max_dimension or additional_max > max_dimension:
            logger.warning(
                f"One or more images are large (model: {model_max}px, flatlay: {flatlay_max}px, "
                f"additional: {additional_max}px). Resizing to {max_dimension}px to avoid API issues."
            )
            
            # Resize images if too large (maintain aspect ratio)
            if model_max > max_dimension:
                ratio = max_dimension / model_max
                new_size = (int(model_image.size[0] * ratio), int(model_image.size[1] * ratio))
                model_image = model_image.resize(new_size, Image.Resampling.LANCZOS)
                logger.info(f"Resized model image to: {model_image.size}")
            
            if flatlay_max > max_dimension:
                ratio = max_dimension / flatlay_max
                new_size = (int(flatlay_image.size[0] * ratio), int(flatlay_image.size[1] * ratio))
                flatlay_image = flatlay_image.resize(new_size, Image.Resampling.LANCZOS)
                logger.info(f"Resized flat-lay image to: {flatlay_image.size}")
            
            if additional_image and additional_max > max_dimension:
                ratio = max_dimension / additional_max
                new_size = (int(additional_image.size[0] * ratio), int(additional_image.size[1] * ratio))
                additional_image = additional_image.resize(new_size, Image.Resampling.LANCZOS)
                logger.info(f"Resized additional image to: {additional_image.size}")
        
        # Convert images to RGB to ensure compatibility (some formats may cause issues)
        if model_image.mode != 'RGB':
            logger.info(f"Converting model image from {model_image.mode} to RGB")
            model_image = model_image.convert('RGB')
        if flatlay_image.mode != 'RGB':
            logger.info(f"Converting flat-lay image from {flatlay_image.mode} to RGB")
            flatlay_image = flatlay_image.convert('RGB')
        if additional_image and additional_image.mode != 'RGB':
            logger.info(f"Converting additional image from {additional_image.mode} to RGB")
            additional_image = additional_image.convert('RGB')
        
        # Prepare content for API
        contents = [
            prompt,
            model_image,
            flatlay_image,
        ]
        if additional_image:
            contents.append(additional_image)
            logger.info("Additional image included in API call (3 images total)")
        else:
            logger.info("No additional image (2 images total)")
        
        # Log request details for debugging
        logger.info(f"Request details: {len(contents)} items (1 prompt + {len(contents)-1} images)")
        logger.info(f"Prompt length: {len(prompt)} characters")
        total_pixels = sum(img.size[0] * img.size[1] for img in contents[1:])
        logger.info(f"Total image pixels: {total_pixels:,}")
        
        # Make API call
        logger.info("Calling Gemini API...")
        response = self.client.models.generate_content(
            model=self.config.model_name,
            contents=contents,
        )
        
        # Extract and save image
        if not response.candidates:
            logger.error("API returned no candidates")
            return None
        
        candidate = response.candidates[0]
        if not candidate or not hasattr(candidate, 'content'):
            logger.error("API candidate has no content")
            if hasattr(response, 'text') and response.text:
                logger.error(f"API response text: {response.text}")
            return None
        
        content = candidate.content
        
        # Content might be None - check why
        if content is None:
            logger.error("API candidate.content is None")
            finish_reason = None
            if hasattr(candidate, 'finish_reason'):
                finish_reason = candidate.finish_reason
                logger.error(f"Finish reason: {finish_reason}")
                
                # Handle different finish reasons
                finish_str = str(finish_reason)
                
                if 'PROHIBITED_CONTENT' in finish_str:
                    logger.error("PROHIBITED_CONTENT: Generation blocked by content policy.")
                    logger.error("Possible causes:")
                    logger.error("  - Images contain content that violates safety policies")
                    logger.error("  - Prompt language triggers content filters")
                    logger.error("  - Combination of images and prompt is flagged")
                    logger.error("Solutions:")
                    logger.error("  - Try different images (avoid sensitive content)")
                    logger.error("  - Simplify or rephrase the prompt")
                    logger.error("  - Ensure images are appropriate for fashion/lifestyle content")
                    raise Exception(
                        "PROHIBITED_CONTENT: The API blocked this generation due to content policy. "
                        "This usually means:\n"
                        "- Images may contain sensitive content\n"
                        "- Prompt language triggered safety filters\n"
                        "- Try using different images or simplifying the prompt"
                    )
                elif 'IMAGE_OTHER' in finish_str:
                    logger.error("IMAGE_OTHER: API had issues generating image. Possible causes:")
                    logger.error("  - Images too large or incompatible format")
                    logger.error("  - Prompt too complex")
                    logger.error("  - API resource limitations")
                    logger.error("  - Try resizing images or simplifying prompt")
                elif 'SAFETY' in finish_str:
                    logger.error("SAFETY: Generation blocked by safety filters")
                    raise Exception(
                        "SAFETY: Generation was blocked by safety filters. "
                        "Try using different images or adjusting the prompt."
                    )
            
            if hasattr(response, 'text') and response.text:
                logger.error(f"API response text: {response.text[:500]}")
            
            # If we haven't raised an exception yet, return None
            return None
        
        if not hasattr(content, 'parts'):
            logger.error("API content has no 'parts' attribute")
            finish_reason = None
            if hasattr(candidate, 'finish_reason'):
                finish_reason = candidate.finish_reason
                logger.error(f"Finish reason: {finish_reason}")
                if 'IMAGE_OTHER' in str(finish_reason):
                    logger.error("IMAGE_OTHER: API had issues generating image")
            return None
        
        for part in content.parts:
            if part.inline_data:
                image_bytes = part.inline_data.data
                generated_image = Image.open(BytesIO(image_bytes))
                
                # Ensure output directory exists
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Save with appropriate format and quality
                save_kwargs = {}
                if self.config.output_format.lower() == "jpg" or self.config.output_format.lower() == "jpeg":
                    # Convert to RGB if necessary for JPEG
                    if generated_image.mode in ("RGBA", "LA", "P"):
                        # Create white background
                        background = Image.new("RGB", generated_image.size, (255, 255, 255))
                        if generated_image.mode == "P":
                            generated_image = generated_image.convert("RGBA")
                        background.paste(generated_image, mask=generated_image.split()[-1] if generated_image.mode in ("RGBA", "LA") else None)
                        generated_image = background
                    save_kwargs["quality"] = self.config.output_quality
                    save_kwargs["optimize"] = True
                
                # Resize output if requested
                if max_output_size and max_output_size > 0:
                    current_max = max(generated_image.size)
                    if current_max > max_output_size:
                        ratio = max_output_size / current_max
                        new_size = (int(generated_image.size[0] * ratio), int(generated_image.size[1] * ratio))
                        logger.info(f"Resizing output from {generated_image.size} to {new_size} (max dimension: {max_output_size}px)")
                        generated_image = generated_image.resize(new_size, Image.Resampling.LANCZOS)
                    elif current_max < max_output_size:
                        # Only upscale if significantly smaller (avoid quality loss)
                        logger.info(f"Image size ({current_max}px) is smaller than requested ({max_output_size}px), keeping original size")
                
                generated_image.save(output_path, format=self.config.output_format.upper(), **save_kwargs)
                logger.info(f"Image saved: {output_path} ({generated_image.size}, {generated_image.mode})")
                return output_path
        
        # If we get here, no image was found in the response
        logger.error("API response did not contain image data")
        if hasattr(response, "text") and response.text:
            logger.error(f"API response text: {response.text}")
        return None
    
    def validate_image_quality(self, image_path: Path) -> Tuple[bool, str]:
        """
        Validate that the generated image meets quality standards.
        
        Args:
            image_path: Path to the generated image
            
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            img = Image.open(image_path)
            
            # Check minimum dimensions
            min_dimension = 512
            if min(img.size) < min_dimension:
                return False, f"Image too small: {img.size} (minimum: {min_dimension}px)"
            
            # Check that image was properly saved
            if img.size[0] == 0 or img.size[1] == 0:
                return False, "Invalid image dimensions"
            
            return True, f"Image validated: {img.size}, mode: {img.mode}"
            
        except Exception as e:
            return False, f"Error validating image: {e}"
    
    def generate_ai_model(
        self,
        reference_image_path: Path,
        prompt: str,
        output_path: Path,
    ) -> Optional[Path]:
        """
        Generate an AI model inspired by reference image with different face.
        
        Args:
            reference_image_path: Path to the reference model image
            prompt: The prompt describing the desired AI model
            output_path: Path where the output image should be saved
            
        Returns:
            Path to the saved output image if successful, None otherwise
        """
        # Validate input file exists
        if not reference_image_path.exists():
            logger.error(f"Reference image not found: {reference_image_path}")
            raise FileNotFoundError(f"Reference image not found: {reference_image_path}")
        
        logger.info(f"Generating AI model from reference: {reference_image_path.name}")
        
        try:
            reference_image = Image.open(reference_image_path)
            
            # Log image info
            logger.info(
                f"Reference image: {reference_image.size}, mode: {reference_image.mode}, "
                f"format: {reference_image.format}"
            )
            
            # Resize if needed
            max_dimension = 2048
            ref_max = max(reference_image.size)
            
            if ref_max > max_dimension:
                logger.warning(
                    f"Reference image is large ({ref_max}px). Resizing to {max_dimension}px to avoid API issues."
                )
                ratio = max_dimension / ref_max
                new_size = (int(reference_image.size[0] * ratio), int(reference_image.size[1] * ratio))
                reference_image = reference_image.resize(new_size, Image.Resampling.LANCZOS)
                logger.info(f"Resized reference image to: {reference_image.size}")
            
            # Convert to RGB
            if reference_image.mode != 'RGB':
                logger.info(f"Converting reference image from {reference_image.mode} to RGB")
                reference_image = reference_image.convert('RGB')
            
            # Prepare content for API
            contents = [prompt, reference_image]
            
            # Log request details
            logger.info(f"Request details: {len(contents)} items (1 prompt + 1 image)")
            logger.info(f"Prompt length: {len(prompt)} characters")
            
            # Make API call
            logger.info("Calling Gemini API to generate AI model...")
            response = self.client.models.generate_content(
                model=self.config.model_name,
                contents=contents,
            )
            
            # Extract and save image (similar to swap_garment logic)
            if not response.candidates:
                logger.error("API returned no candidates")
                return None
            
            candidate = response.candidates[0]
            if not candidate or not hasattr(candidate, 'content'):
                logger.error("API candidate has no content")
                return None
            
            content = candidate.content
            
            if content is None:
                logger.error("API candidate.content is None")
                if hasattr(candidate, 'finish_reason'):
                    finish_reason = candidate.finish_reason
                    logger.error(f"Finish reason: {finish_reason}")
                return None
            
            if not hasattr(content, 'parts'):
                logger.error("API content has no 'parts' attribute")
                return None
            
            for part in content.parts:
                if part.inline_data:
                    image_bytes = part.inline_data.data
                    generated_image = Image.open(BytesIO(image_bytes))
                    
                    # Ensure output directory exists
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Save with appropriate format
                    save_kwargs = {}
                    if self.config.output_format.lower() in ("jpg", "jpeg"):
                        # Convert to RGB if necessary for JPEG
                        if generated_image.mode in ("RGBA", "LA", "P"):
                            background = Image.new("RGB", generated_image.size, (255, 255, 255))
                            if generated_image.mode == "P":
                                generated_image = generated_image.convert("RGBA")
                            background.paste(generated_image, mask=generated_image.split()[-1] if generated_image.mode in ("RGBA", "LA") else None)
                            generated_image = background
                        save_kwargs["quality"] = self.config.output_quality
                        save_kwargs["optimize"] = True
                    
                    generated_image.save(output_path, format=self.config.output_format.upper(), **save_kwargs)
                    logger.info(f"✅ AI model saved to: {output_path} ({generated_image.size}, {generated_image.mode})")
                    return output_path
            
            # If we get here, no image was found in the response
            logger.error("API response did not contain image data")
            return None
            
        except Exception as e:
            logger.error(f"Error generating AI model: {e}", exc_info=True)
            raise

