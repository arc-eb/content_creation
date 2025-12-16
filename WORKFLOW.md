# Recommended Workflow for Garment Swapping

## Quick Start Workflow (Recommended)

### Step 1: First Run
Run the quick iteration script to generate your first image:

```bash
python quick_iterate.py porte1.png aplat_rose.png
```

This will:
- Generate an image using the base prompt
- Save it to `test_nanobanana/output/porte1_aplat_rose_swap.png`
- Show you the file path so you can review it in Cursor

### Step 2: Review the Output
- Open the generated image in Cursor
- Compare it to:
  - The original model image (`porte1.png`)
  - The flat-lay image (`aplat_rose.png`)
- Note what needs to be improved

### Step 3: Add Refinements
Edit `prompt_refinement.txt` and add your refinement instructions:

```
The sleeves must be the same color as the flat-lay (pink), not grey
The garment color must match the flat-lay exactly
Keep the model's face identical to the original
```

### Step 4: Run Again
Run the same command again:

```bash
python quick_iterate.py porte1.png aplat_rose.png
```

This time it will use the refinements from `prompt_refinement.txt`.

### Step 5: Iterate
Repeat steps 2-4 until you're satisfied with the result.

---

## Scripts Overview

### 1. `quick_iterate.py` ⭐ (Recommended)
**Use for:** Quick iterations using file-based refinements

**Workflow:**
- Run script → Review output → Edit `prompt_refinement.txt` → Run again

**Best for:** Most use cases, fastest iteration

```bash
python quick_iterate.py <model> <flatlay>
python quick_iterate.py porte1.png aplat_rose.png
```

### 2. `iterate.py`
**Use for:** Interactive step-by-step iteration

**Workflow:**
- Run script → Review output → Type refinements → Automatically runs again

**Best for:** When you want guided, interactive iteration

```bash
python iterate.py <model> <flatlay>
python iterate.py porte1.png aplat_rose.png
```

### 3. `run_and_preview.py`
**Use for:** Quick test with command-line options (no refinements)

**Best for:** Quick tests with different model/flatlay combinations

```bash
python run_and_preview.py --model porte1.png --flatlay aplat_rose.png
python run_and_preview.py --flatlay aplat_torsade.jpg --luxury
```

### 4. `run_single.py`
**Use for:** Simplest single-run (no refinements)

**Best for:** One-off generations

```bash
python run_single.py porte1.png aplat_rose.png
```

---

## Complete Example Workflow

### First Time Using the System

1. **Initial run:**
   ```bash
   python quick_iterate.py porte1.png aplat_rose.png
   ```

2. **Review output:** Check `test_nanobanana/output/porte1_aplat_rose_swap.png`

3. **Identify issues:** 
   - Sleeves are grey instead of pink
   - Color doesn't match flat-lay exactly

4. **Add refinements:** Edit `prompt_refinement.txt`:
   ```
   The sleeves must match the flat-lay color exactly - they should be pink, not grey
   The entire garment color must match the flat-lay image exactly
   ```

5. **Run again:**
   ```bash
   python quick_iterate.py porte1.png aplat_rose.png
   ```

6. **Review new output** - If still not perfect, add more refinements and repeat

7. **Once satisfied:** You can use the final prompt for similar garments

---

## Tips

1. **Start simple:** Begin with the base prompt, then add refinements incrementally
2. **Be specific:** Instead of "fix the color", say "the sleeves must be pink to match the flat-lay"
3. **One issue at a time:** Address major issues first, then fine-tune
4. **Save good refinements:** If you find refinements that work well, keep them in `prompt_refinement.txt`
5. **Reset when needed:** Delete `prompt_refinement.txt` to start fresh with base prompt

---

## File Structure

```
.
├── quick_iterate.py          ← Start here (recommended)
├── iterate.py                ← Alternative interactive version
├── prompt_refinement.txt     ← Edit this to add refinements
├── prompt_generator.py       ← Base prompt logic (advanced)
└── test_nanobanana/
    ├── input/
    │   ├── porte1.png        ← Model image
    │   └── aplat_rose.png    ← Flat-lay image
    └── output/
        └── porte1_aplat_rose_swap.png  ← Generated result
```

---

## Common Refinement Patterns

**Color issues:**
```
The garment color must match the flat-lay exactly - same hue, saturation, and brightness
The sleeves must be [color] to match the flat-lay, not [wrong color]
```

**Texture issues:**
```
Preserve the exact cable knit texture from the flat-lay
The knit pattern must match the flat-lay exactly - do not smooth or blur
```

**Model preservation:**
```
Keep the model's face identical to the original - same features, expression, skin tone
Do not modify the model's pose, body proportions, or stance
```

**Lighting/Background:**
```
Do not change the lighting - keep shadows and highlights exactly as in the original
The background must remain identical to the original model image
```

