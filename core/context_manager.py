import json
import os
from datetime import datetime

class ContextManager:
    def __init__(self):
        self.context_file = 'context_memory.json'
        self.load_context()
        
    def load_context(self):
        if os.path.exists(self.context_file):
            with open(self.context_file, 'r') as f:
                self.context = json.load(f)
        else:
            self.context = {'conversations': [], 'user_preferences': {}}
            
    def save_interaction(self, user_input, assistant_response, context_info):
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'response': assistant_response,
            'context': context_info
        }
        self.context['conversations'].append(interaction)
        self.save_context()
        
    def get_recent_context(self, limit=5):
        return self.context['conversations'][-limit:]
