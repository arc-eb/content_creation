"""
Flask web interface for Bompard garment swapping.
Allows uploading model and flat-lay images, generating swaps, and iterating on prompts.
"""
import os
import shutil
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, url_for
from werkzeug.utils import secure_filename
import uuid

from config import Config
from gemini_client import GeminiGarmentSwapClient
from prompt_generator import PromptGenerator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output_web'
# Get secret key from environment or use default (change in production!)
app.secret_key = os.getenv("SECRET_KEY", "bompard-secret-key-change-in-production")

# Ensure directories exist
Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)
Path(app.config['OUTPUT_FOLDER']).mkdir(exist_ok=True)

# API key must be set in environment for production
if not os.getenv("GEMINI_API_KEY"):
    logger.warning("GEMINI_API_KEY not set in environment. Please set it before deploying.")


def allowed_file(filename):
    """Check if file extension is allowed."""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Main page with upload form."""
    return render_template('index.html')


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok', 'message': 'Server is running'})


@app.route('/generate', methods=['POST'])
def generate():
    """Generate garment swap with optional refinements."""
    try:
        logger.info("Received generation request")
        # Check files
        if 'model_file' not in request.files or 'flatlay_file' not in request.files:
            return jsonify({'error': 'Both model and flat-lay files are required'}), 400
        
        model_file = request.files['model_file']
        flatlay_file = request.files['flatlay_file']
        refinements = request.form.get('refinements', '').strip()
        output_size = request.form.get('output_size', 'original')  # Get output size preference
        
        logger.info(f"Received refinements: {repr(refinements[:100])}")  # Log first 100 chars
        logger.info(f"Output size preference: {output_size}")
        
        if model_file.filename == '' or flatlay_file.filename == '':
            return jsonify({'error': 'Please select both files'}), 400
        
        if not (allowed_file(model_file.filename) and allowed_file(flatlay_file.filename)):
            return jsonify({'error': 'Invalid file type. Allowed: PNG, JPG, JPEG, WEBP'}), 400
        
        # Generate unique session ID
        session_id = str(uuid.uuid4())[:8]
        
        # Save uploaded files
        model_filename = secure_filename(model_file.filename)
        flatlay_filename = secure_filename(flatlay_file.filename)
        
        model_ext = model_filename.rsplit('.', 1)[1].lower()
        flatlay_ext = flatlay_filename.rsplit('.', 1)[1].lower()
        
        model_path = Path(app.config['UPLOAD_FOLDER']) / f"{session_id}_model.{model_ext}"
        flatlay_path = Path(app.config['UPLOAD_FOLDER']) / f"{session_id}_flatlay.{flatlay_ext}"
        
        model_file.save(model_path)
        flatlay_file.save(flatlay_path)
        
        # Get model image dimensions to use as default output size
        try:
            from PIL import Image as PILImage
            with PILImage.open(model_path) as model_img:
                model_max_dimension = max(model_img.size)
                logger.info(f"Model image dimensions: {model_img.size}, max dimension: {model_max_dimension}px")
        except Exception as e:
            logger.warning(f"Could not read model image dimensions: {e}")
            model_max_dimension = None
        
        # Prepare prompt
        prompt_gen = PromptGenerator()
        base_prompt = prompt_gen.generate_garment_swap_prompt()
        
        # Build full prompt with refinements
        if refinements:
            # Remove comments and empty lines from refinements
            clean_refinements = "\n".join(
                line for line in refinements.split("\n") 
                if line.strip() and not line.strip().startswith("#")
            )
            
            logger.info(f"Cleaned refinements (length: {len(clean_refinements)}): {repr(clean_refinements[:200])}")
            
            if clean_refinements.strip():
                # Limit refinement length to avoid API issues
                max_refinement_length = 500
                if len(clean_refinements.strip()) > max_refinement_length:
                    logger.warning(f"Refinements too long ({len(clean_refinements)} chars), truncating to {max_refinement_length}")
                    clean_refinements = clean_refinements.strip()[:max_refinement_length]
                
                full_prompt = base_prompt
                full_prompt += "\n\n"
                full_prompt += "ADDITIONAL REFINEMENTS:"
                full_prompt += "\n"
                full_prompt += clean_refinements.strip()
                
                logger.info("✓ Refinements added to prompt")
                logger.debug(f"Full prompt with refinements:\n{full_prompt}")
            else:
                full_prompt = base_prompt
                logger.info("Refinements were empty after cleaning, using base prompt only")
        else:
            full_prompt = base_prompt
            logger.info("No refinements provided, using base prompt only")
        
        # Log prompt length
        logger.info(f"Final prompt length: {len(full_prompt)} characters")
        logger.info(f"Base prompt length: {len(base_prompt)} characters")
        if refinements:
            logger.info(f"Refinements added: {len(full_prompt) - len(base_prompt)} characters")
        
        # Generate output path
        output_filename = f"{session_id}_result.png"
        output_path = Path(app.config['OUTPUT_FOLDER']) / output_filename
        
        # Initialize and run garment swap
        config = Config.from_env()
        config.ensure_directories()
        client = GeminiGarmentSwapClient(config)
        
        print(f"Generating garment swap: {model_path} + {flatlay_path}")
        print(f"Output: {output_path}")
        print(f"Prompt length: {len(full_prompt)} characters")
        
        # Parse output size
        # If "original" is selected or no size specified, default to model image size
        max_output_size = None
        if output_size and output_size != 'original':
            try:
                max_output_size = int(output_size)
                logger.info(f"Output will be resized to max {max_output_size}px (user selected)")
            except (ValueError, TypeError):
                logger.warning(f"Invalid output size '{output_size}', using model image size")
                max_output_size = model_max_dimension
        else:
            # Default: match model image size
            max_output_size = model_max_dimension
            if max_output_size:
                logger.info(f"Using default: output will match model image size (max {max_output_size}px)")
        
        try:
            result_path = client.swap_garment(
                model_image_path=model_path,
                flatlay_image_path=flatlay_path,
                prompt=full_prompt,
                output_path=output_path,
                max_output_size=max_output_size,
            )
        except Exception as e:
            logger.error(f"Error in garment swap: {e}", exc_info=True)
            error_msg = str(e)
            
            # Provide user-friendly error messages
            if 'PROHIBITED_CONTENT' in error_msg:
                error_msg = (
                    "Content Policy Error: The API blocked this generation.\n\n"
                    "Possible reasons:\n"
                    "• Images may contain sensitive or inappropriate content\n"
                    "• Prompt language triggered safety filters\n"
                    "• Try using different images or simplifying the prompt\n\n"
                    "For fashion/lifestyle content, ensure images are appropriate and professional."
                )
            elif 'SAFETY' in error_msg:
                error_msg = (
                    "Safety Filter Error: Generation was blocked by safety filters.\n\n"
                    "Try:\n"
                    "• Use different images\n"
                    "• Adjust the prompt language\n"
                    "• Ensure content is appropriate for professional use"
                )
            elif 'IMAGE_OTHER' in error_msg:
                error_msg = (
                    "API returned IMAGE_OTHER error. The API had trouble generating the image.\n\n"
                    "Try:\n"
                    "1. Images may be too large (they will be auto-resized, but try smaller images)\n"
                    "2. Simplify refinements (shorter instructions)\n"
                    "3. Wait a moment and try again (temporary API issue)\n"
                    "4. Try without refinements first, then add them incrementally"
                )
            elif '500' in error_msg or 'INTERNAL' in error_msg:
                error_msg = (
                    "API returned 500 INTERNAL error. Usually temporary.\n\n"
                    "Try: shorter refinements, smaller images, or wait and retry"
                )
            
            return jsonify({'error': error_msg}), 500
        
        if result_path and result_path.exists():
            refinements_applied = bool(refinements and clean_refinements.strip())
            message = 'Image generated successfully!'
            if refinements_applied:
                message += ' (Refinements were applied ✓)'
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'image_url': url_for('get_image', filename=output_filename),
                'message': message,
                'refinements_applied': refinements_applied,
                'prompt_used': full_prompt,  # Send full prompt to frontend
                'base_prompt_length': len(base_prompt),
                'full_prompt_length': len(full_prompt)
            })
        else:
            return jsonify({'error': 'Failed to generate image. Please check the logs.'}), 500
            
    except Exception as e:
        logger.error(f"Error in generate endpoint: {e}", exc_info=True)
        import traceback
        traceback.print_exc()
        error_msg = str(e)
        # Make error message more user-friendly
        if 'content' in error_msg.lower() or 'parts' in error_msg.lower():
            error_msg = "API response error. The model may have returned an unexpected format. Please try again or check the console for details."
        return jsonify({'error': f'Error generating image: {error_msg}'}), 500


@app.route('/image/<filename>')
def get_image(filename):
    """Serve generated images."""
    file_path = Path(app.config['OUTPUT_FOLDER']) / filename
    if file_path.exists():
        return send_file(file_path)
    else:
        return jsonify({'error': 'Image not found'}), 404


if __name__ == '__main__':
    # Get port from environment or default to 5000
    port = int(os.getenv('PORT', 5000))
    # Only run in debug mode if explicitly set
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    print("="*70)
    print(f"Starting Bompard Garment Swap on port {port}")
    print("="*70)
    app.run(host='0.0.0.0', port=port, debug=debug)
    print("Bompard Garment Swap Web Interface")
    print("="*70)
    print("\nStarting server...")
    print("Open your browser and go to: http://127.0.0.1:5000")
    print("\nPress Ctrl+C to stop the server")
    print("="*70)
    app.run(debug=True, host='127.0.0.1', port=5000)

