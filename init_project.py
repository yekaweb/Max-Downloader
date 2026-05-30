#!/usr/bin/env python3
"""
DLBot Project Initialization Script
This script creates the complete project directory structure and all necessary __init__.py files
Run this from the project root directory
"""

import os
from pathlib import Path


def create_package_structure():
    """Create all necessary directories and __init__.py files"""
    
    root_dir = Path.cwd()
    
    # Define all package directories
    packages = {
        "bot": ["middlewares", "handlers", "handlers/admin", "keyboards", "keyboards/inline", "keyboards/reply", "states", "filters"],
        "modules": ["youtube", "instagram", "twitter", "tiktok", "direct_link"],
        "services": [],
        "tasks": [],
        "database": ["models", "repositories"],
        "web": ["routers", "templates", "static", "static/css", "static/js"],
        "locales": ["fa", "en", "ar", "ru", "zh"],
        "utils": [],
        "migrations": ["versions"],
    }
    
    # Non-package directories (just storage)
    storage_dirs = ["logs", "temp_downloads", "cached_files"]
    
    # Create package directories
    for main_pkg, sub_packages in packages.items():
        # Create main package
        pkg_path = root_dir / main_pkg
        pkg_path.mkdir(exist_ok=True)
        
        # Create __init__.py in main package
        init_file = pkg_path / "__init__.py"
        if not init_file.exists():
            init_file.write_text(f'"""{main_pkg.title()} Package"""\n')
        
        # Create sub-packages
        for sub_pkg in sub_packages:
            sub_path = pkg_path / sub_pkg
            sub_path.mkdir(parents=True, exist_ok=True)
            
            # Create __init__.py in sub-package
            sub_init = sub_path / "__init__.py"
            if not sub_init.exists():
                sub_init.write_text(f'"""{sub_pkg.replace("/", " ").title()}"""\n')
    
    # Create storage directories
    for storage_dir in storage_dirs:
        (root_dir / storage_dir).mkdir(exist_ok=True)
    
    print("✅ Project structure created successfully!")
    print(f"📁 Root directory: {root_dir}")
    print(f"📦 Packages created: {', '.join(packages.keys())}")
    print(f"📂 Storage directories created: {', '.join(storage_dirs)}")


if __name__ == "__main__":
    try:
        create_package_structure()
    except Exception as e:
        print(f"❌ Error creating project structure: {e}")
        exit(1)
