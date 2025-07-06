from global_hotkeys import *
import threading

class HotkeyManager:
    def __init__(self, callback):
        self.callback = callback
        self.is_active = False
        
    def setup_hotkeys(self):
        bindings = [
            ["ctrl + alt + space", None, self.activate_assistant, False]
        ]
        register_hotkeys(bindings)
        start_checking_hotkeys()
        
    def activate_assistant(self):
        if not self.is_active:
            self.is_active = True
            self.callback()
