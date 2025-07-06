import json
import os
from datetime import datetime
import pygetwindow as gw
import pyautogui
import pytesseract
from PIL import Image

class ContextManager:
    def __init__(self):
        self.context_file = 'context_memory.json'
        self.load_context()
        
    def load_context(self):
        if os.path.exists(self.context_file):
            try:
                with open(self.context_file, 'r') as f:
                    self.context = json.load(f)
            except:
                self.context = {'conversations': [], 'user_preferences': {}}
        else:
            self.context = {'conversations': [], 'user_preferences': {}}
            
    def save_context(self):
        """Save context to file"""
        try:
            with open(self.context_file, 'w') as f:
                json.dump(self.context, f, indent=2)
        except Exception as e:
            print(f"Error saving context: {e}")
            
    def save_interaction(self, user_input, assistant_response, context_info):
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'response': assistant_response,
            'context': context_info
        }
        self.context['conversations'].append(interaction)
        
        # Keep only last 50 interactions
        if len(self.context['conversations']) > 50:
            self.context['conversations'] = self.context['conversations'][-50:]
            
        self.save_context()
        
    def get_recent_context(self, limit=5):
        return self.context['conversations'][-limit:]
        
    def get_current_screen_context(self):
        """Get current screen context"""
        try:
            # Get active window
            active_window = gw.getActiveWindow()
            if active_window:
                window_info = {
                    'title': active_window.title,
                    'app': active_window.title.split(' - ')[-1] if ' - ' in active_window.title else active_window.title
                }
                
                # Take screenshot of active window
                screenshot = pyautogui.screenshot(region=(
                    active_window.left,
                    active_window.top,
                    active_window.width,
                    active_window.height
                ))
                
                # Extract text from screenshot (optional, requires tesseract)
                try:
                    screen_text = pytesseract.image_to_string(screenshot)
                    window_info['screen_text'] = screen_text[:500]  # Limit text length
                except:
                    window_info['screen_text'] = ""
                    
                return window_info
        except:
            pass
            
        return {'title': 'Unknown', 'app': 'Unknown', 'screen_text': ''}
