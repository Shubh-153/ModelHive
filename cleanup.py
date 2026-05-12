import os
import shutil

def cleanup():
    # Files in root directory
    root_files = ["app.py", "App.jsx"]
    
    # Directories to remove
    dirs = ["output", "__pycache__", "agents/__pycache__"]

    print("🧹 Cleaning up...")

    for f in root_files:
        if os.path.exists(f):
            os.remove(f)
            print(f"  Deleted: {f}")

    for d in dirs:
        if os.path.exists(d):
            shutil.rmtree(d)
            print(f"  Deleted: {d}/")

    print("✅ Cleanup done!")

if __name__ == "__main__":
    cleanup()