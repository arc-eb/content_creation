"""
Helper script to set up directory structure and migrate existing files.
"""
import os
import shutil
from pathlib import Path


def setup_directories(base_dir: str = "."):
    """
    Create the standard directory structure.
    
    Args:
        base_dir: Base directory for the project
    """
    base = Path(base_dir)
    
    directories = [
        base / "input" / "aplat",
        base / "input" / "models",
        base / "output",
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")
    
    print("\n✅ Directory structure ready!")


def migrate_legacy_files(legacy_input_dir: str, base_dir: str = "."):
    """
    Migrate files from legacy structure to new structure.
    
    Moves files from test_nanobanana/input/ to the new structure:
    - aplat-*.jpg, aplat_*.jpg -> input/aplat/
    - porte*.png, model*.png -> input/models/
    
    Args:
        legacy_input_dir: Path to legacy input directory (e.g., "test_nanobanana/input")
        base_dir: Base directory for the project
    """
    legacy_path = Path(legacy_input_dir)
    base = Path(base_dir)
    
    if not legacy_path.exists():
        print(f"⚠️  Legacy directory not found: {legacy_path}")
        return
    
    aplat_dir = base / "input" / "aplat"
    models_dir = base / "input" / "models"
    
    # Ensure directories exist
    aplat_dir.mkdir(parents=True, exist_ok=True)
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # Find and move files
    moved_count = 0
    
    for file_path in legacy_path.iterdir():
        if not file_path.is_file():
            continue
        
        filename = file_path.name.lower()
        
        # Identify flat-lay images (aplat files)
        if filename.startswith("aplat") or "flat" in filename:
            dest = aplat_dir / file_path.name
            if not dest.exists():
                shutil.copy2(file_path, dest)
                print(f"✓ Moved flat-lay: {file_path.name} -> input/aplat/")
                moved_count += 1
            else:
                print(f"⊘ Skipped (exists): {file_path.name}")
        
        # Identify model images (porte/model files)
        elif filename.startswith("porte") or filename.startswith("model"):
            dest = models_dir / file_path.name
            if not dest.exists():
                shutil.copy2(file_path, dest)
                print(f"✓ Moved model: {file_path.name} -> input/models/")
                moved_count += 1
            else:
                print(f"⊘ Skipped (exists): {file_path.name}")
        else:
            print(f"⊘ Unrecognized file (not moved): {file_path.name}")
    
    print(f"\n✅ Migration complete! Moved {moved_count} files.")


if __name__ == "__main__":
    print("Setting up directory structure...")
    setup_directories()
    
    # Check if legacy directory exists and offer migration
    legacy_dir = "test_nanobanana/input"
    if Path(legacy_dir).exists():
        print(f"\n📦 Found legacy directory: {legacy_dir}")
        response = input("Would you like to migrate files to new structure? (y/n): ")
        if response.lower() == 'y':
            migrate_legacy_files(legacy_dir)
        else:
            print("Skipped migration. You can run it later with:")
            print("  python setup_directories.py")
    else:
        print(f"\n⚠️  No legacy directory found at: {legacy_dir}")
        print("You can manually copy files to:")
        print("  - input/aplat/  (for flat-lay images)")
        print("  - input/models/ (for model/pose images)")

