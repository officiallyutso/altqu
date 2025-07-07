import subprocess
import webbrowser
import pyautogui
import os
import platform
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time

class CommandExecutor:
    def __init__(self):
        self.browser_driver = None
        self.setup_browser()
        
    def setup_browser(self):
        """Initialize browser for web automation"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            self.browser_driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print(f"Browser setup failed: {e}")
            
    def execute_command(self, parsed_command):
        """Execute the parsed command"""
        action_type = parsed_command.get('type')
        
        try:
            if action_type == 'open_application':
                self.launch_application(parsed_command.get('app'))
            elif action_type == 'web_search':
                self.perform_web_search(parsed_command.get('query'))
            elif action_type == 'web_navigate':
                self.navigate_to_url(parsed_command.get('url'))
            elif action_type == 'create_document':
                self.create_document(parsed_command)
            elif action_type == 'file_operation':
                self.handle_file_operation(parsed_command)
            elif action_type == 'system_control':
                self.execute_system_command(parsed_command.get('command'))
            else:
                print(f"Unknown command type: {action_type}")
                
        except Exception as e:
            print(f"Command execution error: {e}")
            
    def launch_application(self, app_name):
        """Launch applications across platforms"""
        if not app_name:
            return
            
        app_name = app_name.lower()
        system = platform.system().lower()
        
        app_commands = {
            'vscode': {
                'windows': 'code',
                'darwin': 'code',
                'linux': 'code'
            },
            'notepad': {
                'windows': 'notepad',
                'darwin': 'open -a TextEdit',
                'linux': 'gedit'
            },
            'calculator': {
                'windows': 'calc',
                'darwin': 'open -a Calculator',
                'linux': 'gnome-calculator'
            },
            'terminal': {
                'windows': 'cmd',
                'darwin': 'open -a Terminal',
                'linux': 'gnome-terminal'
            }
        }
        
        if app_name in app_commands and system in app_commands[app_name]:
            command = app_commands[app_name][system]
            subprocess.run(command.split(), shell=True)
        else:
            # Try direct execution
            subprocess.run([app_name], shell=True)
            
    def perform_web_search(self, query):
        """Perform web search"""
        if query:
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(search_url)
            
    def navigate_to_url(self, url):
        """Navigate to specific URL"""
        if url:
            webbrowser.open(url)
            
    def create_document(self, command_data):
        """Create various types of documents"""
        doc_type = command_data.get('doc_type')
        
        if doc_type == 'google_doc':
            webbrowser.open('https://docs.google.com/document/create')
        elif doc_type == 'email':
            recipient = command_data.get('recipient', '')
            subject = command_data.get('subject', '')
            content = command_data.get('content', '')
            
            # Create mailto URL
            mailto_url = f"mailto:{recipient}?subject={subject}&body={content}"
            webbrowser.open(mailto_url)
        elif doc_type == 'google_form':
            webbrowser.open('https://forms.google.com/create')
        else:
            # Default to Google Docs
            webbrowser.open('https://docs.google.com/document/create')
            
    def handle_file_operation(self, command_data):
        """Handle file operations"""
        operation = command_data.get('operation')
        file_path = command_data.get('file_path')
        
        if operation == 'open' and file_path:
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', file_path])
            else:
                subprocess.run(['xdg-open', file_path])
                
    def execute_system_command(self, command):
        """Execute system commands safely"""
        if command:
            subprocess.run(command, shell=True)
            
    def fill_google_form(self, form_url, form_data):
        """Fill out Google Forms automatically"""
        if not self.browser_driver:
            self.setup_browser()
            
        try:
            self.browser_driver.get(form_url)
            time.sleep(2)
            
            # Find and fill form fields
            for field_name, value in form_data.items():
                try:
                    field = self.browser_driver.find_element(By.NAME, field_name)
                    field.clear()
                    field.send_keys(value)
                except:
                    # Try by placeholder or label
                    try:
                        field = self.browser_driver.find_element(By.XPATH, f"//input[@placeholder='{field_name}']")
                        field.clear()
                        field.send_keys(value)
                    except:
                        continue
                        
            print("Form filled successfully")
            
        except Exception as e:
            print(f"Form filling error: {e}")
