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
        
    def set_screen_intelligence(self, screen_intelligence):
        self.screen_intelligence = screen_intelligence
        
    def process_intelligent_command(self, user_input, screen_analysis):
        """Process command with full screen understanding"""
        
        # Create comprehensive context
        context = self.build_intelligent_context(screen_analysis)
        
        system_prompt = f"""You are an extremely intelligent desktop AI assistant with full screen awareness and control capabilities.

CURRENT SCREEN CONTEXT:
- Application: {context['current_app']}
- Visible Text: {context['screen_text'][:1000]}
- UI Elements: {len(context['ui_elements']['buttons'])} buttons, {len(context['ui_elements']['text_fields'])} text fields
- Clickable Areas: {len(context['clickable_areas'])} detected

CAPABILITIES:
1. SCREEN INTERACTION: Click any element, type text, scroll, drag
2. APPLICATION CONTROL: Open apps by searching Windows, control any app
3. WEB AUTOMATION: Navigate websites, fill forms, extract information
4. INTELLIGENT ANALYSIS: Understand content, make recommendations
5. MULTI-STEP TASKS: Plan and execute complex workflows

COMMAND TYPES:
- screen_click: Click specific coordinates or elements
- screen_type: Type text at current cursor or specific field
- app_search_open: Search and open applications like Windows search
- web_intelligent: Intelligent web browsing and interaction
- analyze_and_recommend: Analyze screen content and provide recommendations
- multi_step_task: Execute complex multi-step operations

For Spotify example: "play the best song out of these"
- Analyze visible songs on screen
- Determine which is "best" based on popularity, ratings, or user preferences
- Click on that song

For Amazon example: "find the best product"
- Analyze visible products
- Compare prices, ratings, reviews
- Recommend the best option
- Can navigate to product pages

For app opening: "open calculator"
- Use Windows search (Win key + type)
- Don't just run commands, actually simulate user behavior

Return JSON with this structure:
{{
    "type": "command_type",
    "reasoning": "why this action makes sense",
    "target_element": "description of what to interact with",
    "coordinates": [x, y],
    "text_to_type": "text if typing",
    "app_to_search": "app name if searching",
    "analysis": "screen analysis results",
    "multi_steps": ["step1", "step2", "step3"],
    "confidence": 0.95
}}

User Command: {user_input}
"""

        try:
            response = self.client.chat(
                model=self.model_name,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_input}
                ]
            )
            
            response_text = response['message']['content']
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                parsed_response = json.loads(json_match.group())
                return self.enhance_response_with_intelligence(parsed_response, screen_analysis)
            else:
                return self.intelligent_fallback(user_input, screen_analysis)
                
        except Exception as e:
            print(f"AI Engine error: {e}")
            return self.intelligent_fallback(user_input, screen_analysis)
    
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
