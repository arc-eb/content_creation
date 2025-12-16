# Web Interface for Garment Swapping

A beautiful web interface for the Bompard garment swapping tool. Upload images, generate swaps, and iterate on prompts directly in your browser.

## Features

- 📸 **Easy File Upload** - Drag & drop or click to upload model and flat-lay images
- 🎨 **Live Preview** - See your uploaded images before generation
- ✏️ **Prompt Iteration** - Add refinement instructions in a text box
- 🚀 **One-Click Generation** - Generate images with a single click
- 📊 **Visual Feedback** - See loading states and results immediately

## Installation

1. Install Flask (if not already installed):
```bash
pip install Flask
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

## Usage

### Start the Web Server

```bash
python app.py
```

The server will start on `http://127.0.0.1:5000`

### Open in Browser

Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

### Workflow

1. **Upload Images:**
   - Click "Choose File" or drag & drop the model image (porte)
   - Click "Choose File" or drag & drop the flat-lay image (aplat)
   - Images will be previewed automatically

2. **First Generation:**
   - (Optional) Leave refinement instructions empty for first run
   - Click "🚀 Generate Garment Swap"
   - Wait 30-60 seconds for generation

3. **Review Result:**
   - The generated image will appear below
   - Review it carefully

4. **Iterate:**
   - Add refinement instructions in the text box
   - Examples:
     - "The sleeves must be pink, not grey"
     - "Make the garment color match the flat-lay exactly"
     - "Keep the model's face identical to the original"
   - Click "🚀 Generate Garment Swap" again
   - Repeat until satisfied

## File Structure

```
.
├── app.py                    # Flask web application
├── templates/
│   └── index.html           # Web interface
├── uploads/                  # Temporary uploaded files (auto-created)
└── output_web/              # Generated images (auto-created)
```

## API Key

Make sure your `GEMINI_API_KEY` environment variable is set, or the app will use the hardcoded key (for development only).

```bash
export GEMINI_API_KEY='your-api-key-here'
```

## Tips

- **First generation:** Leave refinements empty to see base result
- **Be specific:** Instead of "fix color", say "sleeves must be pink to match flat-lay"
- **Iterate incrementally:** Make small changes, test, then refine further
- **Review carefully:** Compare output to both input images

## Troubleshooting

**Port already in use:**
- Change the port in `app.py`: `app.run(port=5001)`

**File upload fails:**
- Check file size (max 16MB)
- Ensure files are images (PNG, JPG, JPEG, WEBP)

**Generation fails:**
- Check console/terminal for error messages
- Verify API key is set correctly
- Check that images are valid

## Stopping the Server

Press `Ctrl+C` in the terminal to stop the web server.

