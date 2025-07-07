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
            print("✓ Global hotkeys registered (Alt+q)")
        else:
            print("✗ Failed to register global hotkeys")
            
        print("✓ Super Intelligent Desktop AI Assistant ready!")
        print("✓ Screen analysis and computer vision enabled")
        print("✓ Intelligent command processing active")
        print("Press Alt+q to activate the super intelligent assistant")
        
    def show_assistant(self):
        """Show the chat interface immediately and perform screen analysis asynchronously"""
        # Show interface immediately - FAST!
        self.root.after(0, self.chat_interface.show_interface)
        
        # Perform screen analysis in background thread
        def analyze_screen():
            try:
                screen_analysis = self.screen_intelligence.capture_and_analyze_screen()
                # Update the interface with analysis results when ready
                self.root.after(0, lambda: self.chat_interface.set_current_screen_analysis(screen_analysis))
            except Exception as e:
                print(f"Screen analysis error: {e}")
        
        # Start analysis in background thread
        threading.Thread(target=analyze_screen, daemon=True).start()
        
    def run(self):
        """Run the main application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nShutting down Super Intelligent AI Assistant...")
            self.shutdown()
    
    def handle_exception(exc_type, exc_value, exc_traceback):
        """Global exception handler"""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        print(f"Uncaught exception: {exc_type.__name__}: {exc_value}")

    # Set global exception handler
    sys.excepthook = handle_exception

            
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
