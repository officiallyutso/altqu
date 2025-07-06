import sys
import os
import threading
import time
import tkinter as tk
from core.ai_engine import AIEngine
from core.executor import CommandExecutor
from core.context_manager import ContextManager
from core.hotkey_manager import HotkeyManager
from ui.chat_interface import ChatInterface

class DesktopAIAssistant:
    def __init__(self):
        print("Initializing Desktop AI Assistant...")
        
        # Initialize Tkinter root first
        self.root = tk.Tk()
        self.root.withdraw()  # Hide initially
        
        # Initialize components
        self.context_manager = ContextManager()
        self.ai_engine = AIEngine()
        self.executor = CommandExecutor()
        self.chat_interface = ChatInterface(
            self.ai_engine, 
            self.executor, 
            self.context_manager,
            self.root  # Pass root to chat interface
        )
        self.hotkey_manager = HotkeyManager(self.show_assistant)
        
        # Setup hotkeys
        if self.hotkey_manager.setup_hotkeys():
            print("✓ Global hotkeys registered (Ctrl+Alt+Space)")
        else:
            print("✗ Failed to register global hotkeys")
            
        print("✓ Desktop AI Assistant ready!")
        print("Press Ctrl+Alt+Space to activate the assistant")
        
    def show_assistant(self):
        """Show the chat interface - thread-safe version"""
        # Use after() to schedule GUI update in main thread
        self.root.after(0, self.chat_interface.show_interface)
        
    def run(self):
        """Run the main application with Tkinter mainloop"""
        try:
            # Start Tkinter main loop
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nShutting down AI Assistant...")
            self.shutdown()
            
    def shutdown(self):
        """Clean shutdown"""
        self.hotkey_manager.stop_hotkeys()
        if self.executor.browser_driver:
            self.executor.browser_driver.quit()
        self.root.quit()
        sys.exit(0)

if __name__ == "__main__":
    # Check if Ollama is running
    try:
        import ollama
        client = ollama.Client()
        client.list()  # Test connection
        print("✓ Ollama connection successful")
    except Exception as e:
        print(f"✗ Ollama connection failed: {e}")
        print("Please make sure Ollama is running and LLaMA 3 is installed:")
        print("1. Install Ollama: https://ollama.com/")
        print("2. Run: ollama pull llama3")
        print("3. Start Ollama service")
        sys.exit(1)
    
    # Start the assistant
    assistant = DesktopAIAssistant()
    assistant.run()


def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    print(f"Uncaught exception: {exc_type.__name__}: {exc_value}")

# Set global exception handler
sys.excepthook = handle_exception
