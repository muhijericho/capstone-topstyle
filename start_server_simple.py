#!/usr/bin/env python
"""Simple script to clear cache and start Django server"""
import os
import shutil
import subprocess
import sys

# Clear Python cache
print("Clearing Python cache...")
for root, dirs, files in os.walk('.'):
    # Remove __pycache__ directories
    if '__pycache__' in dirs:
        pycache_path = os.path.join(root, '__pycache__')
        try:
            shutil.rmtree(pycache_path)
            print(f"Removed: {pycache_path}")
        except:
            pass
    # Remove .pyc files
    for file in files:
        if file.endswith('.pyc'):
            try:
                os.remove(os.path.join(root, file))
            except:
                pass

print("Cache cleared!")
print("\nStarting Django server...")
print("=" * 50)

# Start server
try:
    subprocess.run([sys.executable, 'manage.py', 'runserver'], check=True)
except KeyboardInterrupt:
    print("\nServer stopped.")
except Exception as e:
    print(f"Error: {e}")























