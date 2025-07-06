import cv2
import numpy as np
import pyautogui
import pytesseract
from PIL import Image
import easyocr
import base64
import requests
import json

class ScreenIntelligence:
    def __init__(self):
        self.ocr_reader = easyocr.Reader(['en'])
        self.last_screenshot = None
        self.screen_elements = {}
        
    def capture_and_analyze_screen(self):
        """Capture screen and perform comprehensive analysis"""
        screenshot = pyautogui.screenshot()
        
        # Convert to different formats for analysis
        cv_image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        analysis = {
            'screenshot': screenshot,
            'text_content': self.extract_all_text(screenshot),
            'ui_elements': self.detect_ui_elements(cv_image),
            'clickable_areas': self.find_clickable_elements(cv_image),
            'current_app': self.identify_current_application(),
            'screen_layout': self.analyze_screen_layout(cv_image)
        }
        
        return analysis
    
    def extract_all_text(self, screenshot):
        """Extract all text from screen using multiple OCR methods"""
        # Method 1: Tesseract
        tesseract_text = pytesseract.image_to_string(screenshot)
        
        # Method 2: EasyOCR (better for various fonts)
        easyocr_results = self.ocr_reader.readtext(np.array(screenshot))
        easyocr_text = ' '.join([result[1] for result in easyocr_results])
        
        # Combine and clean results
        all_text = f"{tesseract_text}\n{easyocr_text}"
        return self.clean_extracted_text(all_text)
    
    def detect_ui_elements(self, cv_image):
        """Detect buttons, text fields, and other UI elements"""
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # Detect buttons using template matching and contours
        buttons = self.find_buttons(gray)
        text_fields = self.find_text_fields(gray)
        images = self.find_images(cv_image)
        
        return {
            'buttons': buttons,
            'text_fields': text_fields,
            'images': images
        }
    
    def find_clickable_elements(self, cv_image):
        """Find all clickable elements on screen"""
        clickable_elements = []
        
        # Use computer vision to find clickable areas
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # Find contours that might be clickable
        contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if 100 < area < 10000:  # Filter by reasonable button sizes
                x, y, w, h = cv2.boundingRect(contour)
                clickable_elements.append({
                    'position': (x + w//2, y + h//2),
                    'bounds': (x, y, w, h),
                    'area': area
                })
        
        return clickable_elements
    
    def identify_current_application(self):
        """Identify what application is currently active"""
        try:
            import pygetwindow as gw
            active_window = gw.getActiveWindow()
            if active_window:
                return {
                    'title': active_window.title,
                    'app_name': self.extract_app_name(active_window.title),
                    'bounds': (active_window.left, active_window.top, active_window.width, active_window.height)
                }
        except:
            pass
        return {'title': 'Unknown', 'app_name': 'Unknown', 'bounds': None}
    
    def extract_app_name(self, window_title):
        """Extract application name from window title"""
        common_apps = {
            'spotify': 'Spotify',
            'chrome': 'Google Chrome',
            'firefox': 'Firefox',
            'code': 'VS Code',
            'notepad': 'Notepad',
            'excel': 'Excel',
            'word': 'Word',
            'outlook': 'Outlook',
            'discord': 'Discord',
            'slack': 'Slack'
        }
        
        title_lower = window_title.lower()
        for key, app_name in common_apps.items():
            if key in title_lower:
                return app_name
        
        return window_title.split(' - ')[0] if ' - ' in window_title else window_title
