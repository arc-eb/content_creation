import os
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
from IPython.display import Image as IpyImage, display

MY_API_KEY = os.getenv("GEMINI_API_KEY", "")  # Get from environment variable


# -------------------------------------------------

def edit_image_with_nano_banana(api_key, base_image, reference_image, prompt, output_image_path):
    """
    Uploads two images (model and flat-lay) and applies a prompt to swap the garment.
    
    :param api_key: Your Gemini API Key.
    :param base_image: The image of the model/pose (the model's garment will be replaced).
    :param reference_image: The image of the flat-lay product (the new garment).
    :param prompt: The instruction for garment swapping.
    :param output_image_path: Path to save the generated image.
    """
    if not api_key or api_key == "YOUR_ACTUAL_API_KEY_HERE":
        print("FATAL ERROR: Please set your API key in the MY_API_KEY variable.")
        return

    try:
        client = genai.Client(api_key=api_key)

        # 1. Load both input images
        print(f"\n--- Processing: {os.path.basename(base_image)} ---")
        base_to_edit = Image.open(base_image)
        reference_garment = Image.open(reference_image)

        # 2. Define the model and contents (Prompt + TWO Images)
        model_name = "gemini-2.5-flash-image"
        
        # We include the prompt, the base image, AND the reference image.
        contents = [
            prompt,
            base_to_edit,
            reference_garment,
        ]

        print(f"Requesting garment swap onto model from: {os.path.basename(base_image)}")
        
        # 3. Call the API
        response = client.models.generate_content(
            model=model_name,
            contents=contents,
        )

        # 4. Process and save the result
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                image_bytes = part.inline_data.data
                generated_image = Image.open(BytesIO(image_bytes))
                
                # Create output directory if it doesn't exist
                output_dir = os.path.dirname(output_image_path)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True) 
                    print(f"Created output directory: {output_dir}")

                generated_image.save(output_image_path)
                print(f"✅ Successfully saved new image to: {output_image_path}")
                return output_image_path # Return the path for display

        print("❌ API returned a text response or an error, no image data found.")
        print(response.text)
        return None

    except FileNotFoundError:
        print(f"Error: Required file not found. Check if {base_image} and {reference_image} exist.")
        return None
    except genai.errors.APIError as e:
        print(f"Gemini API Error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

# --- Configuration ---
# All paths are relative to your notebook's directory, inside the 'input' folder
INPUT_DIR = "test_nanobanana/input"
OUTPUT_DIR = "test_nanobanana/output"

# 1. The garment to be swapped IN
FLAT_LAY_PRODUCT = os.path.join(INPUT_DIR, "aplat-colmontant.jpg") #"aplat_gilet.jpg" aplat-sans-manche aplat_torsade #aplat_torsade.jpg

# 2. The poses/models to swap ONTO
POSE_IMAGES = [
    os.path.join(INPUT_DIR, "porte1.png"),
    os.path.join(INPUT_DIR, "porte2.png"),
    os.path.join(INPUT_DIR, "porte3.png"),
]

# The precise prompt to instruct the garment replacement
GARMENT_SWAP_PROMPT = (
"""Professional fashion photography of a model wearing this exact beige cable-knit cashmere turtleneck sweater.
   The sweater features prominent vertical cable patterns, a high rolled neck, and long sleeves with ribbed cuffs.
   GARMENT DETAILS: Natural beige/sand color, thick Irish cable knit texture, relaxed fit, luxurious cashmere material.
   POSE: Model standing in elegant casual pose,
   one hand gently touching the collar or in pocket,
   natural relaxed posture showcasing the sweater's texture and drape.
   STYLING: Paired with neutral tailored trousers or jeans, minimal jewelry.
   LIGHTING: Soft diffused studio lighting with gentle shadows to emphasize the cable knit texture,
   warm color temperature to complement the beige tone. BACKGROUND: Clean white or soft neutral backdrop,
   professional studio setting.
   MOOD: Sophisticated French luxury, cozy elegance, timeless Bompard aesthetic. 
   Camera: Medium shot (waist up) or 3/4 length, slight angle, professional fashion editorial style.
   keep the exact same model face."""  
)
# ---------------------

if __name__ == "__main__":
    generated_files = []
    
    print(f"Starting Garment Swap for {len(POSE_IMAGES)} poses using product: {FLAT_LAY_PRODUCT}")
    
    # Loop through all the pose images
    for i, pose_file in enumerate(POSE_IMAGES):
        # Create a unique output file name for each result
        pose_name = os.path.splitext(os.path.basename(pose_file))[0] # e.g., 'porte1'
        output_name = f"{pose_name}_swapped_sweat.png"
        output_path = os.path.join(OUTPUT_DIR, output_name)
        
        # Call the modified function with two image inputs
        result_path = edit_image_with_nano_banana(
            MY_API_KEY, 
            base_image=pose_file, 
            reference_image=FLAT_LAY_PRODUCT, 
            prompt=GARMENT_SWAP_PROMPT, 
            output_image_path=output_path
        )
        
        if result_path:
            generated_files.append(result_path)

    # 6. Display all output images in the notebook
    if generated_files:
        print("\n" + "="*40)
        print("Final Results Display:")
        print("="*40)
        
        for file_path in generated_files:
            try:
                # Display each image with a controlled width
                print(f"Displaying: {os.path.basename(file_path)}")
                display(IpyImage(filename=file_path, width=300))
            except FileNotFoundError:
                print(f"Display Error: File {file_path} was saved but could not be loaded for display.")
    else:
        print("\nNo images were successfully generated.")