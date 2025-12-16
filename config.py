"""
Configuration management for Bompard content creation tool.
Handles environment variables, API keys, and directory structure.
"""
import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

# Load environment variables from .env file (for local development)
try:
    from dotenv import load_dotenv
    from pathlib import Path
    # Load .env file from the project root directory
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
except ImportError:
    pass  # python-dotenv not installed, skip (use environment variables instead)


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
        # Ensure .env file is loaded (call this every time to be safe)
        env_path = Path(__file__).parent / '.env'
        if env_path.exists():
            try:
                from dotenv import load_dotenv
                # Use override=True to ensure values are loaded even if already set
                load_dotenv(dotenv_path=env_path, override=True)
            except ImportError:
                pass  # python-dotenv not installed, fall back to manual parsing
            except Exception:
                pass  # load_dotenv failed, will try manual parsing below
            
            # If load_dotenv didn't work or python-dotenv not installed, manually parse .env file as fallback
            try:
                with open(env_path, 'r', encoding='utf-8-sig') as f:  # utf-8-sig handles BOM
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"').strip("'")
                            if key and value:
                                os.environ[key] = value  # Always set, even if already exists
            except Exception:
                pass  # If manual parsing also fails, continue with existing env vars
        
        # Get API key from environment (more secure than hardcoding)
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable not set. "
                "Please set it using: export GEMINI_API_KEY='your-key-here' or create a .env file with GEMINI_API_KEY=..."
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

