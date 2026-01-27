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

# Load environment variables from .env file (for local development)
# This MUST happen before importing Config
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    # Try to use python-dotenv first
    try:
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=env_path, override=True)
    except ImportError:
        pass  # python-dotenv not installed, will use manual parsing
    
    # Manual parsing as fallback (handles BOM and cases where python-dotenv fails)
    try:
        with open(env_path, 'r', encoding='utf-8-sig') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and value:
                        os.environ[key] = value
    except Exception:
        pass  # If parsing fails, continue with existing env vars

from config import Config
from gemini_client import GeminiGarmentSwapClient
from prompt_generator import PromptGenerator
from models import db, Generation, GeneratedImage
import logging
import time
import base64

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output_web'
# Get secret key from environment or use default (change in production!)
app.secret_key = os.getenv("SECRET_KEY", "bompard-secret-key-change-in-production")

# Database configuration
database_url = os.getenv('DATABASE_URL', 'sqlite:///bompard_content.db')
# Handle Render.com's postgres:// URLs (need to convert to postgresql://)
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Create tables
with app.app_context():
    try:
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")

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
    response = app.make_response(render_template('index.html'))
    # Disable caching for development
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


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
        additional_file = request.files.get('additional_image')  # Optional additional image
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
        
        # Handle optional additional image
        additional_path = None
        if additional_file and additional_file.filename != '':
            if not allowed_file(additional_file.filename):
                return jsonify({'error': 'Invalid additional image file type. Allowed: PNG, JPG, JPEG, WEBP'}), 400
            additional_filename = secure_filename(additional_file.filename)
            additional_ext = additional_filename.rsplit('.', 1)[1].lower()
            additional_path = Path(app.config['UPLOAD_FOLDER']) / f"{session_id}_additional.{additional_ext}"
            additional_file.save(additional_path)
            logger.info(f"Additional image saved: {additional_path}")
        
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
                # Limit refinement length to avoid API issues (increased for iterations)
                max_refinement_length = 2000  # Increased to allow multiple iterations
                if len(clean_refinements.strip()) > max_refinement_length:
                    logger.warning(f"Refinements too long ({len(clean_refinements)} chars), truncating to {max_refinement_length}")
                    clean_refinements = clean_refinements.strip()[:max_refinement_length]
                
                full_prompt = base_prompt
                full_prompt += "\n\n"
                
                # If additional image is provided, combine it with refinements in a single note
                if additional_path:
                    full_prompt += "NOTE: An additional image is provided for guidance. Apply these refinement instructions to guide the generation:"
                    full_prompt += "\n"
                    full_prompt += clean_refinements.strip()
                else:
                    full_prompt += "ADDITIONAL REFINEMENTS:"
                    full_prompt += "\n"
                    full_prompt += clean_refinements.strip()
                
                logger.info("✓ Refinements added to prompt")
                if additional_path:
                    logger.info("✓ Additional image note combined with refinements")
                logger.debug(f"Full prompt with refinements:\n{full_prompt}")
            else:
                full_prompt = base_prompt
                logger.info("Refinements were empty after cleaning, using base prompt only")
        else:
            full_prompt = base_prompt
            logger.info("No refinements provided, using base prompt only")
        
        # Add note about additional image if provided (even without refinements)
        if additional_path and not refinements:
            full_prompt += "\n\nNOTE: An additional image is provided. Use it as additional guidance for the generation."
        
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
        
        # Track start time for processing duration
        start_time = time.time()
        
        try:
            result_path = client.swap_garment(
                model_image_path=model_path,
                flatlay_image_path=flatlay_path,
                prompt=full_prompt,
                output_path=output_path,
                max_output_size=max_output_size,
                additional_image_path=additional_path,  # Optional additional image
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
            
            # Save error to database
            try:
                processing_time = time.time() - start_time
                generation = Generation(
                    session_id=session_id,
                    generation_type='garment_swap',
                    model_image_path=str(model_path) if model_path else None,
                    flatlay_image_path=str(flatlay_path) if flatlay_path else None,
                    output_image_path=str(output_path),
                    refinements=refinements if refinements else None,
                    output_size=output_size,
                    prompt_used=full_prompt,
                    success=False,
                    error_message=error_msg,
                    processing_time_seconds=processing_time
                )
                db.session.add(generation)
                db.session.commit()
                logger.info(f"Saved failed garment swap to database (ID: {generation.id})")
            except Exception as db_error:
                logger.error(f"Failed to save error to database: {db_error}")
            
            # Include prompt in error response so user can see what was used
            return jsonify({
                'error': error_msg,
                'prompt_used': full_prompt,
                'base_prompt_length': len(base_prompt),
                'full_prompt_length': len(full_prompt)
            }), 500
        
        if result_path and result_path.exists():
            processing_time = time.time() - start_time
            refinements_applied = bool(refinements and clean_refinements.strip())
            message = 'Image generated successfully!'
            if refinements_applied:
                message += ' (Refinements were applied ✓)'
            
            # Save to database
            try:
                generation = Generation(
                    session_id=session_id,
                    generation_type='garment_swap',
                    model_image_path=str(model_path),
                    flatlay_image_path=str(flatlay_path),
                    output_image_path=str(output_path),
                    refinements=refinements if refinements else None,
                    output_size=output_size,
                    prompt_used=full_prompt,
                    success=True,
                    processing_time_seconds=processing_time
                )
                db.session.add(generation)
                db.session.commit()
                logger.info(f"✅ Saved garment swap generation to database (ID: {generation.id})")
            except Exception as e:
                logger.error(f"Failed to save generation to database: {e}")
                # Don't fail the request if DB write fails
            
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
            return jsonify({
                'error': 'Failed to generate image. Please check the logs.',
                'prompt_used': full_prompt,
                'base_prompt_length': len(base_prompt),
                'full_prompt_length': len(full_prompt)
            }), 500
            
    except Exception as e:
        logger.error(f"Error in generate endpoint: {e}", exc_info=True)
        import traceback
        traceback.print_exc()
        error_msg = str(e)
        # Make error message more user-friendly
        if 'content' in error_msg.lower() or 'parts' in error_msg.lower():
            error_msg = "API response error. The model may have returned an unexpected format. Please try again or check the console for details."
        
        # Include prompt if it was built (may not exist if error occurred early)
        error_response = {'error': f'Error generating image: {error_msg}'}
        if 'full_prompt' in locals():
            error_response['prompt_used'] = full_prompt
            if 'base_prompt' in locals():
                error_response['base_prompt_length'] = len(base_prompt)
                error_response['full_prompt_length'] = len(full_prompt)
        
        return jsonify(error_response), 500


@app.route('/generate-ai-model', methods=['POST'])
def generate_ai_model():
    """Generate an AI model inspired by the uploaded model image."""
    try:
        logger.info("Received AI model generation request")
        
        # Validate reference image
        if 'reference_model' not in request.files:
            return jsonify({'error': 'Reference model image required'}), 400
        
        reference_file = request.files['reference_model']
        
        if reference_file.filename == '':
            return jsonify({'error': 'Please select a reference image'}), 400
        
        if not allowed_file(reference_file.filename):
            return jsonify({'error': 'Invalid file type. Allowed: PNG, JPG, JPEG, WEBP'}), 400
        
        # Generate unique session ID
        session_id = str(uuid.uuid4())[:8]
        
        # Save reference image temporarily
        ref_filename = secure_filename(reference_file.filename)
        ref_ext = ref_filename.rsplit('.', 1)[1].lower()
        ref_path = Path(app.config['UPLOAD_FOLDER']) / f"{session_id}_reference.{ref_ext}"
        reference_file.save(ref_path)
        
        logger.info(f"Reference image saved: {ref_path}")
        
        # Get custom instructions if provided
        custom_instructions = request.form.get('custom_instructions', '').strip()
        if custom_instructions:
            logger.info(f"Custom instructions provided: {repr(custom_instructions[:100])}")
        
        # Generate AI model prompt
        prompt_gen = PromptGenerator()
        ai_model_prompt = prompt_gen.generate_ai_model_prompt(custom_instructions=custom_instructions if custom_instructions else None)
        
        logger.info(f"AI model prompt length: {len(ai_model_prompt)} characters")
        
        # Output path for AI model
        ai_model_filename = f"{session_id}_ai_model.png"
        ai_model_path = Path(app.config['OUTPUT_FOLDER']) / ai_model_filename
        
        # Initialize and call Gemini API
        config = Config.from_env()
        config.ensure_directories()
        client = GeminiGarmentSwapClient(config)
        
        print(f"Generating AI model from: {ref_path}")
        print(f"Output: {ai_model_path}")
        
        # Track start time
        start_time = time.time()
        
        try:
            result_path = client.generate_ai_model(
                reference_image_path=ref_path,
                prompt=ai_model_prompt,
                output_path=ai_model_path
            )
        except Exception as e:
            logger.error(f"Error in AI model generation: {e}", exc_info=True)
            error_msg = str(e)
            
            # Provide user-friendly error messages
            if 'API_IMAGE_OTHER' in error_msg or 'IMAGE_OTHER' in error_msg:
                error_msg = (
                    "⚠️ API Generation Issue\n\n"
                    "The Gemini API couldn't complete this modification (IMAGE_OTHER error). "
                    "This can happen randomly with face/pose modifications.\n\n"
                    "Solutions:\n"
                    "• Click 'Generate Different Model' to try again\n"
                    "• Simplify your custom instructions\n"
                    "• Try a different reference image\n"
                    "• Sometimes it works on the 2nd or 3rd try"
                )
            elif 'PROHIBITED_CONTENT' in error_msg:
                error_msg = (
                    "Content Policy Error: The API blocked this generation.\n\n"
                    "The reference image may contain content that violates safety policies. "
                    "Try using a different reference image."
                )
            elif 'SAFETY' in error_msg:
                error_msg = (
                    "Safety Filter Error: Generation was blocked by safety filters.\n\n"
                    "Try using a different reference image."
                )
            
            # Save error to database
            try:
                processing_time = time.time() - start_time
                generation = Generation(
                    session_id=session_id,
                    generation_type='ai_model',
                    model_image_path=str(ref_path),
                    output_image_path=str(ai_model_path),
                    custom_instructions=custom_instructions if custom_instructions else None,
                    prompt_used=ai_model_prompt,
                    success=False,
                    error_message=error_msg,
                    processing_time_seconds=processing_time
                )
                db.session.add(generation)
                db.session.commit()
                logger.info(f"Saved failed AI model generation to database (ID: {generation.id})")
            except Exception as db_error:
                logger.error(f"Failed to save error to database: {db_error}")
            
            return jsonify({'error': error_msg}), 500
        
        if result_path and result_path.exists():
            processing_time = time.time() - start_time
            
            # Save to database
            try:
                generation = Generation(
                    session_id=session_id,
                    generation_type='ai_model',
                    model_image_path=str(ref_path),
                    output_image_path=str(ai_model_path),
                    custom_instructions=custom_instructions if custom_instructions else None,
                    prompt_used=ai_model_prompt,
                    success=True,
                    processing_time_seconds=processing_time
                )
                db.session.add(generation)
                db.session.commit()
                logger.info(f"✅ Saved AI model generation to database (ID: {generation.id})")
            except Exception as e:
                logger.error(f"Failed to save AI model to database: {e}")
                # Don't fail the request if DB write fails
            
            return jsonify({
                'success': True,
                'ai_model_url': url_for('get_image', filename=ai_model_filename),
                'session_id': session_id,
                'message': 'AI model generated successfully'
            })
        else:
            return jsonify({'error': 'Failed to generate AI model. Please check the logs.'}), 500
            
    except Exception as e:
        logger.error(f"Error in generate-ai-model endpoint: {e}", exc_info=True)
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error generating AI model: {str(e)}'}), 500


@app.route('/image/<filename>')
def get_image(filename):
    """Serve generated images."""
    file_path = Path(app.config['OUTPUT_FOLDER']) / filename
    if file_path.exists():
        response = send_file(file_path)
        # Add cache control for generated images
        response.headers['Cache-Control'] = 'public, max-age=3600'
        return response
    else:
        return jsonify({'error': 'Image not found'}), 404


@app.route('/save-image', methods=['POST'])
def save_image():
    """Save result image binary data to database."""
    try:
        data = request.get_json()
        image_url = data.get('image_url')
        
        if not image_url:
            return jsonify({'error': 'image_url is required'}), 400
        
        # Extract filename from URL (e.g., /image/abc123_result.png -> abc123_result.png)
        filename = image_url.split('/')[-1]
        
        # Read image file from output folder
        image_path = Path(app.config['OUTPUT_FOLDER']) / filename
        
        if not image_path.exists():
            return jsonify({'error': f'Image file not found: {filename}'}), 404
        
        # Read image binary data
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # Save to database
        saved_image = GeneratedImage(image_data=image_data)
        db.session.add(saved_image)
        db.session.commit()
        
        logger.info(f"✅ Saved image to database (ID: {saved_image.id}, size: {len(image_data)} bytes)")
        
        return jsonify({
            'success': True,
            'image_id': saved_image.id,
            'message': 'Image saved to database successfully!'
        })
        
    except Exception as e:
        logger.error(f"Error saving image to database: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/gallery')
def gallery():
    """Render gallery page to view saved images."""
    return render_template('gallery.html')


@app.route('/api/saved-images')
def get_saved_images():
    """Get list of all saved images with thumbnails."""
    try:
        limit = request.args.get('limit', 50, type=int)
        limit = min(limit, 100)  # Max 100
        
        saved_images = GeneratedImage.query.order_by(
            GeneratedImage.created_at.desc()
        ).limit(limit).all()
        
        # Convert to list with base64 thumbnails for display
        images_list = []
        for img in saved_images:
            img_dict = img.to_dict(include_data=True)
            images_list.append(img_dict)
        
        return jsonify({
            'count': len(images_list),
            'images': images_list
        })
        
    except Exception as e:
        logger.error(f"Error fetching saved images: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/saved-image/<int:image_id>')
def get_saved_image(image_id):
    """Get full resolution image by ID."""
    try:
        saved_image = GeneratedImage.query.get(image_id)
        
        if not saved_image:
            return jsonify({'error': 'Image not found'}), 404
        
        # Return image as binary data
        from io import BytesIO
        return send_file(
            BytesIO(saved_image.image_data),
            mimetype='image/png',
            as_attachment=False,
            download_name=f'saved_image_{image_id}.png'
        )
        
    except Exception as e:
        logger.error(f"Error retrieving saved image: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/history/<session_id>')
def get_history(session_id):
    """Get generation history for a specific session."""
    try:
        generations = Generation.query.filter_by(
            session_id=session_id
        ).order_by(Generation.created_at.desc()).limit(20).all()
        
        return jsonify({
            'session_id': session_id,
            'count': len(generations),
            'generations': [g.to_dict() for g in generations]
        })
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/history')
def get_all_history():
    """Get recent generation history (last 50)."""
    try:
        limit = request.args.get('limit', 50, type=int)
        limit = min(limit, 100)  # Max 100
        
        generations = Generation.query.order_by(
            Generation.created_at.desc()
        ).limit(limit).all()
        
        # Calculate statistics
        total_count = Generation.query.count()
        success_count = Generation.query.filter_by(success=True).count()
        
        return jsonify({
            'total_generations': total_count,
            'successful_generations': success_count,
            'success_rate': round(success_count / total_count * 100, 1) if total_count > 0 else 0,
            'recent_count': len(generations),
            'generations': [g.to_dict() for g in generations]
        })
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Get port from environment or default to 5000
    port = int(os.getenv('PORT', 5000))
    # Enable debug mode by default for local development
    # Set FLASK_DEBUG=False to disable
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    # Disable reloader on Windows (causes socket errors on Ctrl+C)
    # You can enable it by setting FLASK_RELOADER=True if needed
    use_reloader = os.getenv('FLASK_RELOADER', 'False').lower() == 'true' and os.name != 'nt'
    
    print("="*70)
    print("Bompard Garment Swap - Virtual Try-On")
    print("="*70)
    print(f"Starting server on port {port}")
    print(f"Debug mode: {debug}")
    print(f"Auto-reloader: {use_reloader}")
    print(f"Template auto-reload: {debug}")
    print(f"Open your browser and go to: http://127.0.0.1:{port}")
    print("\nPress Ctrl+C to stop the server")
    print("Tip: If you don't see changes, do a hard refresh (Ctrl+F5 or Cmd+Shift+R)")
    print("="*70)
    print()
    
    app.run(host='0.0.0.0', port=port, debug=debug, use_reloader=use_reloader)

