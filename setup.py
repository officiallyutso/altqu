import subprocess
import sys
import os

def install_package(package):
    """Install a Python package"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("Setting up Desktop AI Assistant...")
    
    # Required packages
    packages = [
        "ollama",
        "keyboard",
        "pygetwindow",
        "pyautogui", 
        "selenium",
        "webdriver-manager",
        "pytesseract",
        "Pillow",
        "requests"
    ]
    
    print("Installing Python packages...")
    for package in packages:
        print(f"Installing {package}...")
        if install_package(package):
            print(f"✓ {package} installed successfully")
        else:
            print(f"✗ Failed to install {package}")
    
    print("\nSetup complete!")
    print("\nNext steps:")
    print("1. Install Ollama: https://ollama.com/")
    print("2. Run: ollama pull llama3")
    print("3. Run: python main.py")

if __name__ == "__main__":
    main()
