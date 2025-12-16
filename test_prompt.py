"""Quick test to see what prompt is being generated."""
from prompt_generator import PromptGenerator

pg = PromptGenerator()
prompt = pg.generate_garment_swap_prompt()

print("="*80)
print("CURRENT PROMPT:")
print("="*80)
print(prompt)
print("="*80)
print(f"\nPrompt length: {len(prompt)} characters")

