# Bompard Content Creation Tool

Production-grade Python tool for automated luxury cashmere garment swapping using Google's Gemini 2.5 Flash Image model.

## Features

- 🎨 **Photorealistic garment swapping** with texture preservation
- 💎 **Luxury-focused prompt engineering** optimized for cashmere materials
- 🏗️ **Production-ready architecture** with modular design
- 📁 **Structured directory management** (input/aplat, input/models, output)
- 🔒 **Secure configuration** via environment variables
- 📊 **Comprehensive logging** and error handling
- ✅ **Quality validation** for generated images

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your Gemini API key:
```bash
export GEMINI_API_KEY='your-api-key-here'
```

On Windows (PowerShell):
```powershell
$env:GEMINI_API_KEY='your-api-key-here'
```

## Directory Structure

```
.
├── input/
│   ├── aplat/          # Flat-lay garment images
│   └── models/         # Model/pose images
├── output/             # Generated images
├── config.py           # Configuration management
├── prompt_generator.py # Prompt engineering
├── gemini_client.py    # API client
├── main.py            # Main execution script
└── requirements.txt   # Dependencies
```

## Usage

### Basic Usage

Edit `main.py` to specify your input files:

```python
model_images = [
    "porte1.png",
    "porte2.png",
    "porte3.png",
]

flatlay_image = "aplat-colmontant.jpg"

results = processor.process_batch(
    model_images=model_images,
    flatlay_image=flatlay_image,
)
```

Then run:
```bash
python main.py
```

### Advanced Usage

#### Custom Prompts

```python
from prompt_generator import PromptGenerator

# Generate luxury cashmere-specific prompt
custom_prompt = PromptGenerator.generate_luxury_cashmere_prompt(
    color="beige",
    style="turtleneck",
    knit_pattern="cable knit",
)

results = processor.process_batch(
    model_images=model_images,
    flatlay_image=flatlay_image,
    custom_prompt=custom_prompt,
)
```

#### Single Image Processing

```python
result = processor.process_single_swap(
    model_image="porte1.png",
    flatlay_image="aplat-colmontant.jpg",
    output_filename="custom_output.png",
)
```

#### Custom Configuration

```python
from config import Config

# Create config with custom base directory
config = Config.from_env(base_dir="/path/to/project")

# Or create config programmatically
config = Config(
    api_key="your-api-key",
    base_dir=Path("/path/to/project"),
    input_aplat_dir=Path("/custom/aplat/path"),
    input_models_dir=Path("/custom/models/path"),
    output_dir=Path("/custom/output/path"),
)
```

## Configuration Options

The tool supports several configuration options via the `Config` class:

- `api_key`: Gemini API key (required, use environment variable)
- `model_name`: Model to use (default: "gemini-2.5-flash-image")
- `output_format`: Output format "png" or "jpg" (default: "png")
- `output_quality`: JPEG quality 1-100 (default: 95)
- `max_retries`: API retry attempts (default: 3)
- `retry_delay`: Delay between retries in seconds (default: 1.0)

## Prompt Engineering

The `PromptGenerator` class provides sophisticated prompts optimized for:

- **Texture realism**: Captures cashmere fiber details, cable patterns, ribbing
- **Color accuracy**: Precise color matching from flat-lay to model
- **Model preservation**: Keeps face, pose, and proportions identical
- **Lighting integration**: Seamlessly blends garment with original lighting
- **Luxury aesthetic**: Maintains Bompard's sophisticated French luxury brand identity

## Error Handling

The tool includes comprehensive error handling:

- API errors with automatic retries and exponential backoff
- File validation before processing
- Image quality validation after generation
- Detailed logging for debugging

## Logging

Logs are written to console with timestamps. Set log level via:

```python
import logging
logging.basicConfig(level=logging.DEBUG)  # For more verbose output
```

## Migration from Legacy Script

If migrating from `example_creation_from_aplat_to_porte.py`:

1. Move your images to the new structure:
   - Flat-lay images → `input/aplat/`
   - Model images → `input/models/`

2. Update your API key usage:
   - Remove hardcoded API key
   - Set `GEMINI_API_KEY` environment variable

3. Update file references in `main.py` to use just filenames (paths are resolved automatically)

## License

Internal tool for Bompard Paris.

