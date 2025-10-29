#!/usr/bin/env python3
"""
Script to save the handshake image from the chat attachment
Run this script after saving the image as 'handshake_temp.jpg' in the project root
"""

import base64
from pathlib import Path
import shutil

# Source and destination paths
source = Path("handshake_temp.jpg")
dest = Path("assets/handshake.jpg")

# Create assets directory if it doesn't exist
dest.parent.mkdir(exist_ok=True)

if source.exists():
    # Copy the file
    shutil.copy(source, dest)
    print(f"✅ Image saved to {dest}")
    print(f"📏 File size: {dest.stat().st_size / 1024:.2f} KB")
    
    # Optional: Clean up temp file
    # source.unlink()
else:
    print(f"❌ Source file not found: {source}")
    print("Please save the handshake image as 'handshake_temp.jpg' in the project root first")
    print("\nAlternatively, directly save the image to: assets/handshake.jpg")
