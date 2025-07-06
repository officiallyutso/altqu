# main.py (updated)
import sys
import os
import threading
import time
import tkinter as tk
from core.super_ai_engine import SuperAIEngine
from core.intelligent_executor import IntelligentExecutor
from core.context_manager import ContextManager
from core.hotkey_manager import HotkeyManager
from core.screen_intelligence import ScreenIntelligence
from ui.chat_interface import ChatInterface

class SuperIntelligentDesktopAssistant:
    def __init__(self):
        print("Initializing Super Intelligent Desktop AI Assistant...")
        
        # Initialize Tkinter root first
        self.root = tk.Tk()
        self.root.withdraw()
        
        # Initialize intelligent components
        self.screen_intelligence = ScreenIntelligence()
        self.context_manager = ContextManager()
        self.ai_engine = SuperAIEngine()
        self.ai_engine.set_screen_intelligence(self.screen_intelligence)
        self.executor = IntelligentExecutor()
        
        self.chat_interface = ChatInterface(
            self.ai_engine,
            self.executor,
            self.context_manager,
            self.root,
            self.screen_intelligence  # Pass screen intelligence
        )
        
        self.hotkey_manager = HotkeyManager(self.show_assistant)
        
        # Setup hotkeys
        if self.hotkey_manager.setup_hotkeys():
            print("✓ Global hotkeys registered (Ctrl+Alt+Space)")
        else:
            print("✗ Failed to register global hotkeys")
            
        print("✓ Super Intelligent Desktop AI Assistant ready!")
        print("✓ Screen analysis and computer vision enabled")
        print("✓ Intelligent command processing active")
        print("Press Ctrl+Alt+Space to activate the super intelligent assistant")
        
    def show_assistant(self):
        """Show the chat interface with screen analysis"""
        # Analyze screen before showing interface
        screen_analysis = self.screen_intelligence.capture_and_analyze_screen()
        self.chat_interface.set_current_screen_analysis(screen_analysis)
        
        # Show interface
        self.root.after(0, self.chat_interface.show_interface)
        
    def run(self):
        """Run the main application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nShutting down Super Intelligent AI Assistant...")
            self.shutdown()
            
    def shutdown(self):
        """Clean shutdown"""
        self.hotkey_manager.stop_hotkeys()
        if self.executor.browser_driver:
            self.executor.browser_driver.quit()
        self.root.quit()
        sys.exit(0)

if __name__ == "__main__":
    # Check dependencies
    try:
        import ollama
        import cv2
        import easyocr
        import pytesseract
        
        client = ollama.Client()
        client.list()
        print("✓ All dependencies available")
    except Exception as e:
        print(f"✗ Missing dependencies: {e}")
        print("Please install: pip install opencv-python easyocr pytesseract")
        sys.exit(1)
    
    # Start the super intelligent assistant
    assistant = SuperIntelligentDesktopAssistant()
    assistant.run()
