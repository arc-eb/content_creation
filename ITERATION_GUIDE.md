# Prompt Iteration Guide

This guide explains how to iterate on prompts to improve garment swap results.

## Quick Start

### Method 1: Interactive Iteration Tool

Use the interactive tool to iterate step-by-step:

```bash
python iterate.py porte1.png aplat_rose.png
```

This will:
1. Generate an image with the base prompt
2. Show you the result
3. Ask for refinement instructions
4. Generate again with refinements
5. Repeat until you're satisfied

### Method 2: File-Based Iteration (Recommended for Quick Iterations)

1. **First run:**
   ```bash
   python quick_iterate.py porte1.png aplat_rose.png
   ```

2. **Review the output image**

3. **Edit `prompt_refinement.txt`** with your refinement instructions:
   ```
   Make the garment color match the flat-lay more precisely
   Keep the model's expression exactly as in the original image
   Preserve the exact texture from the flat-lay without smoothing
   ```

4. **Run again:**
   ```bash
   python quick_iterate.py porte1.png aplat_rose.png
   ```

5. **Repeat steps 2-4** until satisfied

## Refinement Instructions Examples

### Common Issues and Solutions

**Issue: Garment color doesn't match flat-lay**
```
The garment color must match the flat-lay image exactly - same hue, saturation, and brightness.
```

**Issue: Model's face changed**
```
The model's face must be identical to the original - same features, expression, skin tone, hair, makeup.
```

**Issue: Texture not preserved**
```
The garment texture must match the flat-lay exactly - preserve all knit patterns, cable details, and material texture.
```

**Issue: Lighting changed**
```
Do not modify the lighting at all - keep the exact same shadows, highlights, and lighting direction.
```

**Issue: Background changed**
```
The background must remain exactly the same - do not change any background elements.
```

**Issue: Buttons/details missing**
```
All garment details (buttons, patterns, decorative elements) must match the flat-lay image exactly.
```

### Advanced Refinements

**Multiple specific issues:**
```
- The cable knit pattern must be clearly visible and match the flat-lay pattern exactly
- The garment buttons must match the flat-lay buttons (color, size, position)
- Do not smooth or blur the texture - keep it sharp and detailed like the flat-lay
- The garment fit should be natural but the appearance must match the flat-lay exactly
```

## Workflow Tips

1. **Start with base prompt** - Get an initial result first
2. **Review carefully** - Compare output to both input images
3. **Be specific** - Clearly describe what needs to change
4. **Iterate incrementally** - Make small changes, test, then refine further
5. **Save good prompts** - Once you find a good refinement, you can save it for similar garments

## File Structure

- `prompt_refinement.txt` - Your refinement instructions (edit this)

## Resetting Refinements

To start fresh, either:
- Delete `prompt_refinement.txt`
- Or run the interactive tool and type "reset" when prompted

## Viewing the Full Prompt

To see exactly what prompt is being sent to the API:

```bash
python quick_iterate.py porte1.png aplat_rose.png --show-prompt
```

This helps you understand how refinements are being combined with the base prompt.

