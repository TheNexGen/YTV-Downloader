#!/usr/bin/env python3
"""
Build script for YTV Downloader
This script compiles the application and creates a release package.
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

def clean_build_dirs():
    """Clean previous build artifacts"""
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Cleaning {dir_name}...")
            shutil.rmtree(dir_name)

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building executable...")
    
    # Run PyInstaller
    result = subprocess.run([
        sys.executable, '-m', 'PyInstaller', 'main.spec',
        '--clean', '--noconfirm'
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("Build failed!")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return False
    
    print("Build completed successfully!")
    return True

def create_release_package():
    """Create a release package with all necessary files"""
    print("Creating release package...")
    
    # Create release directory
    release_dir = "release"
    if os.path.exists(release_dir):
        shutil.rmtree(release_dir)
    os.makedirs(release_dir)
    
    # Copy executable
    exe_name = "YTV-Downloader.exe" if platform.system() == "Windows" else "YTV-Downloader"
    exe_path = os.path.join("dist", exe_name)
    
    if os.path.exists(exe_path):
        shutil.copy2(exe_path, release_dir)
        print(f"Copied {exe_name} to release directory")
    else:
        print(f"Warning: {exe_name} not found in dist directory")
    
    # Copy README
    if os.path.exists("README.md"):
        shutil.copy2("README.md", release_dir)
        print("Copied README.md to release directory")
    
    # Create version info file
    version_info = f"""YTV Downloader Release
Version: 1.0.0
Build Date: {platform.system()} {platform.release()}
Python Version: {sys.version}
"""
    
    with open(os.path.join(release_dir, "VERSION.txt"), "w") as f:
        f.write(version_info)
    
    print("Release package created successfully!")
    return True

def main():
    """Main build process"""
    print("=== YTV Downloader Build Process ===")
    
    # Clean previous builds
    clean_build_dirs()
    
    # Build executable
    if not build_executable():
        print("Build failed! Exiting.")
        sys.exit(1)
    
    # Create release package
    if not create_release_package():
        print("Release package creation failed! Exiting.")
        sys.exit(1)
    
    print("\n=== Build Complete ===")
    print("Executable is ready in the 'release' directory")
    print("You can now create a GitHub release with the files in the 'release' directory")

if __name__ == "__main__":
    main() 