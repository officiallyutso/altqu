import pyautogui
import time
import subprocess
import webbrowser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import cv2
import numpy as np

class IntelligentExecutor:
    def __init__(self):
        # Configure pyautogui settings
        pyautogui.FAILSAFE = True  # Keep failsafe enabled for safety
        pyautogui.PAUSE = 0.1  # Reduce pause time for better performance
        
        self.browser_driver = None
        self.setup_browser()
        
    def extract_product_info(self, screen_text):
        """Extract product information from screen text"""
        # Simple product extraction - look for price patterns
        import re
        
        price_patterns = re.findall(r'\$[\d,]+\.?\d*', screen_text)
        
        products = []
        for i, price in enumerate(price_patterns):
            products.append({
                'id': i,
                'price': price,
                'text_context': screen_text[max(0, screen_text.find(price)-50):screen_text.find(price)+50]
            })
        
        return products

    def find_best_product(self, products):
        """Find the best product based on simple heuristics"""
        if not products:
            return None
        
        # Simple heuristic: look for highest rated or best value
        best_product = products[0]
        
        for product in products:
            # Look for rating indicators in context
            context = product.get('text_context', '').lower()
            if 'star' in context or 'rating' in context or 'review' in context:
                best_product = product
                break
        
        return best_product

    def general_screen_analysis(self, screen_text):
        """General screen analysis for unknown contexts"""
        print(f"Analyzing screen content: {len(screen_text)} characters detected")
        
        # Look for common UI elements
        if 'button' in screen_text.lower():
            print("Buttons detected on screen")
        if 'search' in screen_text.lower():
            print("Search functionality detected")
        if 'menu' in screen_text.lower():
            print("Menu elements detected")

    def parse_step_to_command(self, step, screen_analysis):
        """Parse a step into a command structure"""
        step_lower = step.lower()
        
        if 'click' in step_lower:
            return {
                'type': 'screen_click',
                'target_element': step,
                'reasoning': f'Executing step: {step}'
            }
        elif 'type' in step_lower:
            return {
                'type': 'screen_type',
                'text_to_type': step.replace('type', '').strip(),
                'reasoning': f'Executing step: {step}'
            }
        else:
            return {
                'type': 'web_search',
                'query': step,
                'reasoning': f'Executing step: {step}'
            }

    def intelligent_web_interaction(self, command_data):
        """Intelligent web interaction"""
        url = command_data.get('url', '')
        if url:
            webbrowser.open(url)
        else:
            print("No URL provided for web interaction")
    
    
    def setup_browser(self):
        """Setup browser with intelligent options"""
        try:
            from selenium.webdriver.chrome.options import Options
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-logging")
            chrome_options.add_argument("--log-level=3")
            self.browser_driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print(f"Browser setup failed: {e}")
    
    def execute_intelligent_command(self, command_data, screen_analysis):
        """Execute commands with proper error handling"""
        command_type = command_data.get('type')
        
        try:
            if command_type == 'screen_click':
                self.intelligent_click(command_data, screen_analysis)
            elif command_type == 'screen_type':
                self.intelligent_type(command_data, screen_analysis)
            elif command_type == 'app_search_open':
                self.intelligent_app_open(command_data)
            elif command_type == 'analyze_and_recommend':
                self.analyze_and_recommend(command_data, screen_analysis)
            elif command_type == 'web_intelligent':
                self.intelligent_web_interaction(command_data)
            elif command_type == 'multi_step_task':
                self.execute_multi_step_task(command_data, screen_analysis)
            else:
                # Fallback to basic execution
                self.basic_execution_fallback(command_data)
                
        except pyautogui.FailSafeException:
            print("PyAutoGUI fail-safe triggered. Command execution stopped for safety.")
            print("Move mouse away from screen corners to continue using the assistant.")
        except Exception as e:
            print(f"Intelligent execution error: {e}")

    def intelligent_click(self, command_data, screen_analysis):
        """Click with proper fail-safe handling"""
        coordinates = command_data.get('coordinates')
        target_element = command_data.get('target_element', '')
        
        if coordinates:
            try:
                x, y = coordinates
                print(f"Clicking at ({x}, {y}) - {target_element}")
                
                # Move mouse smoothly (more human-like)
                pyautogui.moveTo(x, y, duration=0.3)
                time.sleep(0.1)
                pyautogui.click()
            except pyautogui.FailSafeException:
                print("Click cancelled due to fail-safe trigger")
        else:
            print("No coordinates found for click target")
    
    def intelligent_type(self, command_data, screen_analysis):
        """Type text intelligently"""
        text_to_type = command_data.get('text_to_type', '')
        coordinates = command_data.get('coordinates')
        
        if coordinates:
            # Click on text field first
            x, y = coordinates
            pyautogui.click(x, y)
            time.sleep(0.2)
        
        if text_to_type:
            # Type with human-like speed
            pyautogui.typewrite(text_to_type, interval=0.05)
    
    def intelligent_app_open(self, command_data):
        """Open apps with fail-safe handling"""
        app_name = command_data.get('app_to_search', '')
        
        if app_name:
            try:
                print(f"Opening {app_name} using Windows search...")
                
                # Press Windows key
                pyautogui.press('win')
                time.sleep(0.5)
                
                # Type app name
                pyautogui.typewrite(app_name, interval=0.1)
                time.sleep(1)
                
                # Press Enter to open first result
                pyautogui.press('enter')
            except pyautogui.FailSafeException:
                print("App opening cancelled due to fail-safe trigger")
    
    def analyze_and_recommend(self, command_data, screen_analysis):
        """Analyze screen content and make intelligent recommendations"""
        current_app = screen_analysis.get('current_app', {}).get('app_name', '')
        screen_text = screen_analysis.get('text_content', '')
        
        if 'spotify' in current_app.lower():
            self.spotify_intelligent_analysis(screen_text)
        elif 'amazon' in screen_text.lower():
            self.amazon_intelligent_analysis(screen_text)
        else:
            self.general_screen_analysis(screen_text)
    
    def spotify_intelligent_analysis(self, screen_text):
        """Intelligent Spotify analysis"""
        print("Analyzing Spotify content...")
        
        # Extract song information from screen text
        songs = self.extract_song_info(screen_text)
        
        if songs:
            # Simple heuristic: look for songs with high play counts or familiar artists
            best_song = self.find_best_song(songs)
            print(f"Recommended song: {best_song}")
            
            # Try to click on the recommended song
            self.click_on_song(best_song)
    
    def amazon_intelligent_analysis(self, screen_text):
        """Intelligent Amazon product analysis"""
        print("Analyzing Amazon products...")
        
        # Extract product information
        products = self.extract_product_info(screen_text)
        
        if products:
            best_product = self.find_best_product(products)
            print(f"Recommended product: {best_product}")
    
    def extract_song_info(self, screen_text):
        """Extract song information from Spotify screen"""
        # Simple regex patterns for song extraction
        import re
        
        # Look for patterns like "Song Name - Artist"
        song_patterns = re.findall(r'([A-Za-z0-9\s]+)\s*-\s*([A-Za-z0-9\s]+)', screen_text)
        
        songs = []
        for match in song_patterns:
            songs.append({
                'title': match[0].strip(),
                'artist': match[1].strip()
            })
        
        return songs
    
    def find_best_song(self, songs):
        """Find the best song using simple heuristics"""
        # Simple scoring based on common popular artists/words
        popular_indicators = ['official', 'remix', 'feat', 'ft', 'radio edit']
        
        best_song = None
        best_score = 0
        
        for song in songs:
            score = 0
            song_text = f"{song['title']} {song['artist']}".lower()
            
            for indicator in popular_indicators:
                if indicator in song_text:
                    score += 1
            
            if score > best_score:
                best_score = score
                best_song = song
        
        return best_song or songs[0] if songs else None
    
    def click_on_song(self, song):
        """Try to click on a specific song"""
        if song:
            # Take a new screenshot and try to find the song
            screenshot = pyautogui.screenshot()
            
            # Use OCR to find the song position
            # This is a simplified version - in practice, you'd use more sophisticated matching
            song_text = f"{song['title']}"
            
            # Try to find and click the song
            try:
                location = pyautogui.locateOnScreen(song_text)
                if location:
                    pyautogui.click(location)
                    print(f"Clicked on song: {song['title']}")
            except:
                print(f"Could not locate song: {song['title']}")
    
    def execute_multi_step_task(self, command_data, screen_analysis):
        """Execute complex multi-step tasks"""
        steps = command_data.get('multi_steps', [])
        
        for i, step in enumerate(steps):
            print(f"Executing step {i+1}: {step}")
            
            # Parse each step and execute
            step_command = self.parse_step_to_command(step, screen_analysis)
            self.execute_intelligent_command(step_command, screen_analysis)
            
            # Wait between steps
            time.sleep(1)
    
    def basic_execution_fallback(self, command_data):
        """Fallback to basic execution for unknown commands"""
        if command_data.get('query'):
            search_url = f"https://www.google.com/search?q={command_data['query'].replace(' ', '+')}"
            webbrowser.open(search_url)
