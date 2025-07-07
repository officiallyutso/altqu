import ollama
import json
import re
from datetime import datetime

class SuperAIEngine:
    def __init__(self):
        self.client = ollama.Client()
        self.model_name = "llama3"
        self.conversation_history = []
        self.screen_intelligence = None
        
    def find_best_text_field(self, screen_analysis):
        """Find the best text field to interact with"""
        text_fields = screen_analysis.get('ui_elements', {}).get('text_fields', [])
        
        if text_fields:
            # Return the first text field found
            return text_fields[0]['position']
        
        return None

    def calculate_relevance_score(self, target_description, screen_text, position):
        """Calculate relevance score for click target"""
        # Simple scoring based on text proximity
        target_words = target_description.lower().split()
        screen_words = screen_text.lower().split()
        
        score = 0
        for word in target_words:
            if word in screen_words:
                score += 1
        
        return score

    def extract_app_name_from_command(self, user_input):
        """Extract app name from user command"""
        user_lower = user_input.lower()
        
        # Common app names
        app_names = {
            'calculator': 'calculator',
            'calc': 'calculator',
            'notepad': 'notepad',
            'chrome': 'chrome',
            'firefox': 'firefox',
            'vscode': 'code',
            'vs code': 'code',
            'word': 'word',
            'excel': 'excel',
            'outlook': 'outlook'
        }
        
        for app_key, app_name in app_names.items():
            if app_key in user_lower:
                return app_name
        
        # Extract from "open [app_name]" pattern
        import re
        match = re.search(r'open\s+(\w+)', user_lower)
        if match:
            return match.group(1)
        
        return 'unknown'
        
    def set_screen_intelligence(self, screen_intelligence):
        self.screen_intelligence = screen_intelligence
        
    def process_intelligent_command(self, user_input, screen_analysis):
        """Process command with better JSON handling"""
        
        context = self.build_intelligent_context(screen_analysis)
        
        system_prompt = f"""You are a desktop AI assistant. Return ONLY valid JSON with this exact structure:

    {{
        "type": "command_type",
        "reasoning": "brief explanation",
        "app_to_search": "app_name_if_opening_app",
        "coordinates": [100, 200],
        "text_to_type": "text_if_typing",
        "confidence": 0.9
    }}

    Valid command types: app_search_open, screen_click, screen_type, web_search

    User wants: {user_input}
    Current app: {context.get('current_app', {}).get('app_name', 'Unknown')}

    Return only the JSON object, no other text."""

        try:
            response = self.client.chat(
                model=self.model_name,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_input}
                ]
            )
            
            response_text = response['message']['content'].strip()
            
            # Clean the response to ensure valid JSON
            response_text = self.clean_json_response(response_text)
            
            # Parse JSON with better error handling
            try:
                parsed_response = json.loads(response_text)
                return parsed_response
            except json.JSONDecodeError as e:
                print(f"JSON parsing failed: {e}")
                return self.create_fallback_response(user_input)
                
        except Exception as e:
            print(f"AI Engine error: {e}")
            return self.create_fallback_response(user_input)

    def clean_json_response(self, response_text):
        """Clean AI response to ensure valid JSON"""
        # Remove any text before the first {
        start_idx = response_text.find('{')
        if start_idx != -1:
            response_text = response_text[start_idx:]
        
        # Remove any text after the last }
        end_idx = response_text.rfind('}')
        if end_idx != -1:
            response_text = response_text[:end_idx + 1]
        
        # Fix common JSON issues
        response_text = response_text.replace("'", '"')  # Replace single quotes
        response_text = re.sub(r',\s*}', '}', response_text)  # Remove trailing commas
        response_text = re.sub(r',\s*]', ']', response_text)  # Remove trailing commas in arrays
        
        return response_text

    def create_fallback_response(self, user_input):
        """Create a safe fallback response"""
        user_lower = user_input.lower()
        
        if any(app in user_lower for app in ['spotify', 'chrome', 'calculator', 'notepad']):
            app_name = next((app for app in ['spotify', 'chrome', 'calculator', 'notepad'] if app in user_lower), 'unknown')
            return {
                'type': 'app_search_open',
                'app_to_search': app_name,
                'reasoning': f'User wants to open {app_name}'
            }
        
        return {
            'type': 'web_search',
            'query': user_input,
            'reasoning': 'Fallback to web search'
        }

    
    def build_intelligent_context(self, screen_analysis):
        """Build comprehensive context from screen analysis"""
        return {
            'current_app': screen_analysis.get('current_app', {}),
            'screen_text': screen_analysis.get('text_content', ''),
            'ui_elements': screen_analysis.get('ui_elements', {}),
            'clickable_areas': screen_analysis.get('clickable_areas', []),
            'screen_layout': screen_analysis.get('screen_layout', {})
        }
    
    def enhance_response_with_intelligence(self, parsed_response, screen_analysis):
        """Enhance AI response with intelligent screen understanding"""
        
        # If AI wants to click something, find the best matching element
        if parsed_response.get('type') == 'screen_click':
            target = parsed_response.get('target_element', '')
            coordinates = self.find_best_click_target(target, screen_analysis)
            if coordinates:
                parsed_response['coordinates'] = coordinates
        
        # If AI wants to type, find the best text field
        elif parsed_response.get('type') == 'screen_type':
            text_field = self.find_best_text_field(screen_analysis)
            if text_field:
                parsed_response['coordinates'] = text_field
        
        return parsed_response
    
    def find_best_click_target(self, target_description, screen_analysis):
        """Find the best element to click based on description"""
        clickable_areas = screen_analysis.get('clickable_areas', [])
        screen_text = screen_analysis.get('text_content', '')
        
        # Use fuzzy matching to find the best target
        best_match = None
        best_score = 0
        
        for element in clickable_areas:
            # Extract text near this clickable area
            x, y = element['position']
            
            # Simple scoring based on proximity to relevant text
            score = self.calculate_relevance_score(target_description, screen_text, (x, y))
            
            if score > best_score:
                best_score = score
                best_match = element['position']
        
        return best_match
    
    def intelligent_fallback(self, user_input, screen_analysis):
        """Intelligent fallback when JSON parsing fails"""
        user_lower = user_input.lower()
        
        # Spotify intelligence
        if 'spotify' in screen_analysis.get('current_app', {}).get('app_name', '').lower():
            if 'play' in user_lower and 'best' in user_lower:
                return {
                    'type': 'analyze_and_recommend',
                    'reasoning': 'User wants to play the best song from visible options',
                    'analysis': 'Analyzing visible songs on Spotify'
                }
        
        # Amazon intelligence
        elif 'amazon' in screen_analysis.get('screen_text', '').lower():
            if 'best product' in user_lower or 'find best' in user_lower:
                return {
                    'type': 'analyze_and_recommend',
                    'reasoning': 'User wants to find the best product from visible options',
                    'analysis': 'Analyzing visible products on Amazon'
                }
        
        # App opening intelligence
        elif 'open' in user_lower or 'launch' in user_lower:
            app_name = self.extract_app_name_from_command(user_input)
            return {
                'type': 'app_search_open',
                'app_to_search': app_name,
                'reasoning': f'User wants to open {app_name} using Windows search'
            }
        
        return {
            'type': 'web_search',
            'query': user_input,
            'reasoning': 'Fallback to web search'
        }
