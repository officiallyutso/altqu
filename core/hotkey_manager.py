import keyboard
import threading
import time

class HotkeyManager:
    def __init__(self, callback):
        self.callback = callback
        self.is_active = False
        self.hotkey_combination = "alt+q"
        
    def setup_hotkeys(self):
        """Setup global hotkeys using keyboard library"""
        try:
            keyboard.add_hotkey(self.hotkey_combination, self.activate_assistant)
            print(f"Hotkey {self.hotkey_combination} registered successfully")
            return True
        except Exception as e:
            print(f"Failed to register hotkey: {e}")
            return False
            
    def activate_assistant(self):
        """Activate assistant - this runs in background thread"""
        if not self.is_active:
            self.is_active = True
            try:
                # Call the callback (which should use root.after() for thread safety)
                self.callback()
            except Exception as e:
                print(f"Error activating assistant: {e}")
            finally:
                # Reset after a short delay
                threading.Timer(0.5, self._reset_active_state).start()
                
    def _reset_active_state(self):
        self.is_active = False
        
    def stop_hotkeys(self):
        """Stop listening for hotkeys"""
        try:
            keyboard.unhook_all_hotkeys()
        except:
            pass
