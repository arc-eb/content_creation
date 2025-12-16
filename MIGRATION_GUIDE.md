# Migration Guide: Legacy to Production Code

This guide helps you migrate from `example_creation_from_aplat_to_porte.py` to the new production-ready structure.

## Quick Start

1. **Set up your API key** (no more hardcoding!):
   ```bash
   export GEMINI_API_KEY='your-api-key-here'
   ```

2. **Run the setup script** to create directories and migrate files:
   ```bash
   python setup_directories.py
   ```

3. **Run the main script**:
   ```bash
   python main.py
   ```

## Key Changes

### 1. Directory Structure

**Old structure:**
```
test_nanobanana/
  input/
    aplat-colmontant.jpg
    porte1.png
    porte2.png
    porte3.png
  output/
```

**New structure:**
```
input/
  aplat/
    aplat-colmontant.jpg
  models/
    porte1.png
    porte2.png
    porte3.png
output/
```

The setup script (`setup_directories.py`) can automatically migrate your files.

### 2. API Key Management

**Old way (INSECURE - hardcoded):**
```python
MY_API_KEY = "your-api-key-here"  # Replace with your actual key
```

**New way (SECURE - environment variable):**
```bash
export GEMINI_API_KEY='your-api-key-here'
```

### 3. Code Structure

**Old way:** Single file with everything mixed together

**New way:** Modular structure:
- `config.py` - Configuration management
- `prompt_generator.py` - Sophisticated prompt engineering
- `gemini_client.py` - API client with error handling
- `main.py` - Main orchestration script

### 4. Usage Patterns

**Old way:**
```python
edit_image_with_nano_banana(
    MY_API_KEY, 
    base_image=pose_file, 
    reference_image=FLAT_LAY_PRODUCT, 
    prompt=GARMENT_SWAP_PROMPT, 
    output_image_path=output_path
)
```

**New way:**
```python
from config import Config
from main import GarmentSwapProcessor

config = Config.from_env()
processor = GarmentSwapProcessor(config)

result = processor.process_single_swap(
    model_image="porte1.png",
    flatlay_image="aplat-colmontant.jpg",
)
```

### 5. Prompt Engineering

**Old prompt:** Basic description

**New prompt:** Sophisticated prompt with:
- Texture realism emphasis
- Color accuracy instructions
- Model preservation directives
- Lighting integration guidelines
- Quality requirements

See `prompt_generator.py` for details.

## Backward Compatibility

The new code includes backward compatibility with the legacy directory structure. If the new structure doesn't exist, it will automatically use `test_nanobanana/input/` and `test_nanobanana/output/`.

However, it's recommended to migrate to the new structure for better organization.

## Step-by-Step Migration

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set your API key:**
   ```bash
   export GEMINI_API_KEY='your-actual-api-key'
   ```

3. **Run setup script:**
   ```bash
   python setup_directories.py
   ```
   This will:
   - Create the new directory structure
   - Optionally migrate files from the legacy structure

4. **Update your workflow:**
   - Edit `main.py` to specify your input files
   - Or use the API programmatically (see `example_usage.py`)

5. **Run:**
   ```bash
   python main.py
   ```

## Troubleshooting

### "GEMINI_API_KEY environment variable not set"
Solution: Set the environment variable before running:
```bash
export GEMINI_API_KEY='your-key'
```

### Files not found
Solution: Ensure files are in the correct directories:
- Flat-lay images → `input/aplat/`
- Model images → `input/models/`

Or run `python setup_directories.py` to migrate automatically.

### Import errors
Solution: Ensure you're in the project directory and dependencies are installed:
```bash
pip install -r requirements.txt
```

## Benefits of New Structure

1. **Security**: API key in environment variable, not hardcoded
2. **Modularity**: Easy to test and maintain
3. **Error Handling**: Comprehensive logging and retries
4. **Quality**: Image validation after generation
5. **Flexibility**: Easy to customize prompts and settings
6. **Production-Ready**: Proper logging, error handling, configuration management

