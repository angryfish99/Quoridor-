import os

def check_structure():
    required_files = [
        "requirements.txt",
        "src/constants.py",
        "src/pathfinding.py",
        "src/models.py"  # We are about to create this
    ]
    for file in required_files:
        if os.path.exists(file):
            print(f"[OK] {file}")
        else:
            print(f"[MISSING] {file}")

if __name__ == "__main__":
    check_structure()
