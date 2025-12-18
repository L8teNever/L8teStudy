import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OLD_DIR = os.path.join(BASE_DIR, 'static', 'uploads')
NEW_DIR = os.path.join(BASE_DIR, 'instance', 'uploads')

def migrate():
    if not os.path.exists(OLD_DIR):
        print(f"Old directory {OLD_DIR} does not exist. Nothing to migrate.")
        return

    if not os.path.exists(NEW_DIR):
        os.makedirs(NEW_DIR)
        print(f"Created new directory {NEW_DIR}")

    files = os.listdir(OLD_DIR)
    for f in files:
        src = os.path.join(OLD_DIR, f)
        dst = os.path.join(NEW_DIR, f)
        if os.path.isfile(src):
            shutil.move(src, dst)
            print(f"Moved {f}")
    
    # Try to remove emptiness
    try:
        os.rmdir(OLD_DIR)
        print("Removed old directory.")
    except Exception as e:
        print(f"Could not remove old directory (might not be empty): {e}")

if __name__ == "__main__":
    migrate()
