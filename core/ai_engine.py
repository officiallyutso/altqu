import ollama
import json
import re
from datetime import datetime

class AIEngine:
    def __init__(self):
        self.client = ollama.Client()
        self.model_name = "llama3"
        self.conversation_history = []
        
    def process_command(self, user_input, context=None):
        """Process natural language command and return structured action"""
        system_prompt = """You are a desktop AI assistant that converts natural language commands into structured JSON actions. 

Available action types:
- open_application: Launch apps like VS Code, browser, etc.
- web_search: Search Google or specific sites
- web_navigate: Open specific URLs or YouTube videos
- create_document: Create Google Docs, emails, etc.
- file_operation: File/folder management
- system_control: System commands

Return ONLY a JSON object with this structure:
{
    "type": "action_type",
    "app": "application_name",
    "query": "search_query",
    "url": "web_url",
    "doc_type": "document_type",
    "recipient": "email_recipient",
    "subject": "email_subject",
    "content": "content_text",
    "file_path": "path",
    "command": "system_command"
}

Examples:
"Open YouTube and play a specific video" -> {"type": "web_navigate", "url": "https://youtube.com/results?search_query=specific video"}
"Launch VS Code" -> {"type": "open_application", "app": "vscode"}
"Search this question online" -> {"type": "web_search", "query": "this question"}
"Create a new Google Doc" -> {"type": "create_document", "doc_type": "google_doc"}
"Write an email to John" -> {"type": "create_document", "doc_type": "email", "recipient": "John"}"""

        try:
            response = self.client.chat(
                model=self.model_name,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': f"Context: {context}\nCommand: {user_input}"}
                ]
            )
            
            # Extract JSON from response
            response_text = response['message']['content']
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            
            if json_match:
                return json.loads(json_match.group())
            else:
                # Fallback parsing
                return self.fallback_parse(user_input)
                
        except Exception as e:
            print(f"AI Engine error: {e}")
            return self.fallback_parse(user_input)
    
    def fallback_parse(self, user_input):
        """Simple fallback parsing for common commands"""
        user_input_lower = user_input.lower()
        
        if "youtube" in user_input_lower and "play" in user_input_lower:
            query = user_input_lower.replace("open youtube and play", "").replace("play", "").strip()
            return {"type": "web_navigate", "url": f"https://youtube.com/results?search_query={query}"}
        elif "vscode" in user_input_lower or "vs code" in user_input_lower:
            return {"type": "open_application", "app": "vscode"}
        elif "search" in user_input_lower:
            query = user_input_lower.replace("search", "").replace("online", "").strip()
            return {"type": "web_search", "query": query}
        elif "google doc" in user_input_lower:
            return {"type": "create_document", "doc_type": "google_doc"}
        elif "email" in user_input_lower:
            return {"type": "create_document", "doc_type": "email"}
        else:
            return {"type": "web_search", "query": user_input}
