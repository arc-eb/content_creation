"""
Configuration management for Bompard content creation tool.
Handles environment variables, API keys, and directory structure.
"""
import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class Config:
    """Application configuration settings."""
    
    # API Configuration
    api_key: str
    base_dir: Path
    input_aplat_dir: Path
    input_models_dir: Path
    output_dir: Path
    
    # Optional settings with defaults
    model_name: str = "gemini-2.5-flash-image"
    output_format: str = "png"  # 'png' or 'jpg'
    output_quality: int = 95  # For JPEG (1-100)
    max_retries: int = 3
    retry_delay: float = 1.0  # seconds
    
    @classmethod
    def from_env(cls, base_dir: Optional[str] = None, legacy_support: bool = True) -> "Config":
        """
        Create configuration from environment variables.
        
        Args:
            base_dir: Base directory path. Defaults to current working directory.
            legacy_support: If True, falls back to legacy directory structure if new structure doesn't exist.
            
        Returns:
            Config instance with settings from environment or defaults.
        """
        # Get API key from environment (more secure than hardcoding)
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable not set. "
                "Please set it using: export GEMINI_API_KEY='your-key-here'"
            )
        
        # Determine base directory
        if base_dir is None:
            base_dir = Path.cwd()
        else:
            base_dir = Path(base_dir)
        
        # Define directory structure
        input_aplat_dir = base_dir / "input" / "aplat"
        input_models_dir = base_dir / "input" / "models"
        output_dir = base_dir / "output"
        
        # Legacy directory support (backward compatibility)
        if legacy_support:
            legacy_input_dir = base_dir / "test_nanobanana" / "input"
            legacy_output_dir = base_dir / "test_nanobanana" / "output"
            
            # Use legacy directories if new structure doesn't exist but legacy does
            if not input_aplat_dir.exists() and legacy_input_dir.exists():
                input_aplat_dir = legacy_input_dir
                input_models_dir = legacy_input_dir
            if not output_dir.exists() and legacy_output_dir.exists():
                output_dir = legacy_output_dir
        
        return cls(
            api_key=api_key,
            base_dir=base_dir,
            input_aplat_dir=input_aplat_dir,
            input_models_dir=input_models_dir,
            output_dir=output_dir,
        )
    
    def ensure_directories(self) -> None:
        """Create all necessary directories if they don't exist."""
        self.input_aplat_dir.mkdir(parents=True, exist_ok=True)
        self.input_models_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def get_output_path(self, model_filename: str, aplat_filename: str) -> Path:
        """
        Generate output path for a garment swap result.
        
        Args:
            model_filename: Name of the model image file
            aplat_filename: Name of the flat-lay image file
            
        Returns:
            Path object for the output file
        """
        model_stem = Path(model_filename).stem
        aplat_stem = Path(aplat_filename).stem
        
        output_filename = f"{model_stem}_{aplat_stem}_swap.{self.output_format}"
        return self.output_dir / output_filename

