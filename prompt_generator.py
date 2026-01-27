"""
Prompt engineering module for luxury cashmere garment swapping.
Optimized for texture realism and Bompard aesthetic.
"""
from typing import Optional


class PromptGenerator:
    """Generates sophisticated prompts for luxury cashmere garment swapping."""
    
    @staticmethod
    def generate_garment_swap_prompt(
        garment_description: Optional[str] = None,
        preserve_face: bool = True,
        preserve_lighting: bool = True,
        preserve_background: bool = True,
    ) -> str:
        """
        Generate a sophisticated prompt for photorealistic garment swapping.
        
        Args:
            garment_description: Optional specific garment details (color, style, etc.)
            preserve_face: Whether to preserve the model's exact face
            preserve_lighting: Whether to preserve original studio lighting
            preserve_background: Whether to preserve original background
            
        Returns:
            Formatted prompt string optimized for Gemini 2.5 Flash Image
        """
        
        # Use the exact style of the original working prompt - describe desired output
        # Start with explicit task instruction, then describe what the output should look like
        # The original format was: "Professional fashion photography of a model wearing [garment]..."
        
        # Ultra-explicit prompt for garment swap
        # Structure: Task definition, then what stays the same, then what changes
        base_instruction = """TASK: You have images - (1) a photo of a model, (2) a flat-lay photo of a garment.
Replace ONLY the clothing on the model with the garment from the flat-lay image.
Everything else in the image must remain identical."""
        
        # What must stay EXACTLY the same
        preservation_lines = []
        
        if preserve_face:
            preservation_lines.append("DO NOT CHANGE: The model's face - keep it identical (same features, expression, skin tone, hair, makeup).")
        
        preservation_lines.append("DO NOT CHANGE: The model's pose, body, proportions, posture, position, or stance.")
        
        if preserve_lighting:
            preservation_lines.append("DO NOT CHANGE: The lighting - keep it identical (same direction, intensity, shadows, highlights).")
        
        if preserve_background:
            preservation_lines.append("DO NOT CHANGE: The background - keep it identical.")
        
        # What must change
        garment_instruction = """ONLY CHANGE: The garment. Replace the model's current clothing with the garment from the flat-lay image.

CRITICAL: The garment from the flat-lay must NOT be modified in any way when transferring to the model.
- Use the garment EXACTLY as shown in the flat-lay image
- Same color, same texture, same patterns, same knit structure, same buttons/details
- Do not alter, adjust, or modify the garment's appearance
- Do not change colors, textures, or patterns
- The garment should fit the model's body naturally, but its visual appearance (color, texture, patterns, details) must match the flat-lay image exactly without any modifications."""
        
        # Build the complete prompt
        prompt_lines = [base_instruction]
        prompt_lines.append("")
        prompt_lines.append("PRESERVE (keep identical):")
        prompt_lines.extend(preservation_lines)
        prompt_lines.append("")
        prompt_lines.append("REPLACE (change this only):")
        prompt_lines.append(garment_instruction)
        prompt_lines.append("")
        prompt_lines.append("Output: Professional fashion photography quality, sharp focus.")
        
        # Join with newlines
        final_prompt = "\n".join(prompt_lines)
        
        return final_prompt
    
    @staticmethod
    def generate_luxury_cashmere_prompt(
        color: Optional[str] = None,
        style: Optional[str] = None,
        knit_pattern: Optional[str] = None,
    ) -> str:
        """
        Generate a luxury cashmere-specific prompt with enhanced texture details.
        
        Args:
            color: Garment color (e.g., "beige", "camel", "charcoal")
            style: Garment style (e.g., "turtleneck", "crew neck", "cardigan")
            knit_pattern: Knit pattern (e.g., "cable knit", "ribbed", "plain")
            
        Returns:
            Specialized prompt for cashmere garments
        """
        
        # Build garment description from parameters
        description_parts = []
        
        if knit_pattern:
            description_parts.append(f"{knit_pattern} pattern")
        
        if color:
            description_parts.append(f"{color} color")
        else:
            description_parts.append("exact color from flat-lay")
        
        if style:
            description_parts.append(f"{style} style")
        
        description = "Luxury cashmere " + ", ".join(description_parts) + "."
        
        if knit_pattern and "cable" in knit_pattern.lower():
            description += " Prominent cable patterns with dimensional depth. Each cable ridge should be clearly defined with shadow and highlight to show 3D texture."
        
        if knit_pattern and "ribbed" in knit_pattern.lower():
            description += " Precise ribbing texture with clearly defined vertical lines showing the knit structure."
        
        description += " The cashmere texture should show the characteristic soft, fine fiber surface with natural luster."
        
        return PromptGenerator.generate_garment_swap_prompt(
            garment_description=description,
            preserve_face=True,
            preserve_lighting=True,
            preserve_background=True,
        )
    
    @staticmethod
    def generate_ai_model_prompt(custom_instructions: Optional[str] = None) -> str:
        """
        Generate prompt for modifying the model's face and pose while keeping style.
        
        Args:
            custom_instructions: Optional custom instructions for model characteristics
        
        Returns:
            Prompt string for face and pose modification
        """
        base_prompt = """TASK: Modify this fashion model photograph by changing the face and adjusting the pose slightly.

REQUIREMENTS:
- CHANGE: Replace the face with a completely different face (photorealistic, professional)
- CHANGE: Adjust the pose slightly - rotate the body or head by 5-15 degrees, or shift the arm/hand position subtly
- KEEP: Same body type and proportions
- KEEP: Same lighting style and background style
- KEEP: Same clothing and overall aesthetic
- KEEP: Professional fashion photography quality

The result should look like a different person in a similar (but not identical) pose, maintaining the same professional fashion photography style."""
        
        # Add custom instructions if provided
        if custom_instructions:
            base_prompt += "\n\nADDITIONAL CUSTOM INSTRUCTIONS:\n"
            base_prompt += custom_instructions.strip()
        
        base_prompt += "\n\nOutput: Modified fashion model photo with different face and slightly adjusted pose."
        
        return base_prompt

