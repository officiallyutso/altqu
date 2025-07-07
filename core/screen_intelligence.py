import cv2
import numpy as np
import pyautogui
import pytesseract
from PIL import Image
import easyocr
import base64
import requests
import json
import re

class ScreenIntelligence:
    def __init__(self):
        self.ocr_reader = easyocr.Reader(['en'])
        self.last_screenshot = None
        self.screen_elements = {}
      
    def capture_and_analyze_screen(self):
        """Optimized screen analysis with error handling"""
        try:
            screenshot = pyautogui.screenshot()
            
            # Resize for faster processing
            original_size = screenshot.size
            screenshot = screenshot.resize((original_size[0] // 3, original_size[1] // 3))
            
            cv_image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            analysis = {
                'screenshot': screenshot,
                'text_content': self.extract_text_fast(screenshot),  # Faster text extraction
                'ui_elements': self.detect_ui_elements_fast(cv_image),  # Simplified detection
                'clickable_areas': self.find_clickable_elements_fast(cv_image),  # Faster detection
                'current_app': self.identify_current_application(),
                'screen_layout': self.analyze_screen_layout(cv_image)
            }
            
            return analysis
        except Exception as e:
            print(f"Screen analysis failed: {e}")
            return self.get_fallback_analysis()

    def extract_text_fast(self, screenshot):
        """Faster text extraction using only one OCR method"""
        try:
            # Use only EasyOCR for better performance
            easyocr_results = self.ocr_reader.readtext(np.array(screenshot))
            text = ' '.join([result[1] for result in easyocr_results])
            return self.clean_extracted_text(text)
        except Exception as e:
            print(f"Fast OCR failed: {e}")
            return ""

    def get_fallback_analysis(self):
        """Fallback analysis when screen capture fails"""
        return {
            'screenshot': None,
            'text_content': "",
            'ui_elements': {'buttons': [], 'text_fields': [], 'images': []},
            'clickable_areas': [],
            'current_app': self.identify_current_application(),
            'screen_layout': {'screen_size': (0, 0), 'regions': {}}
        }
        
    def detect_ui_elements_fast(self, cv_image):
        """Faster UI element detection with simplified processing"""
        try:
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Simplified detection for better performance
            buttons = self.find_buttons_fast(gray)
            text_fields = self.find_text_fields_fast(gray)
            
            return {
                'buttons': buttons,
                'text_fields': text_fields,
                'images': []  # Skip image detection for performance
            }
        except Exception as e:
            print(f"Fast UI element detection failed: {e}")
            return {'buttons': [], 'text_fields': [], 'images': []}

    def find_buttons_fast(self, gray_image):
        """Simplified button detection"""
        try:
            # Use simpler edge detection
            edges = cv2.Canny(gray_image, 100, 200)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            buttons = []
            for contour in contours[:10]:  # Limit to first 10 for performance
                area = cv2.contourArea(contour)
                if 200 < area < 3000:  # Reasonable button sizes
                    x, y, w, h = cv2.boundingRect(contour)
                    buttons.append({
                        'position': (x + w//2, y + h//2),
                        'bounds': (x, y, w, h),
                        'area': area
                    })
            
            return buttons
        except Exception as e:
            print(f"Fast button detection failed: {e}")
            return []

    def find_text_fields_fast(self, gray_image):
        """Simplified text field detection"""
        try:
            # Basic rectangle detection
            contours, _ = cv2.findContours(gray_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            text_fields = []
            for contour in contours[:5]:  # Limit for performance
                area = cv2.contourArea(contour)
                if 500 < area < 5000:
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h
                    if aspect_ratio > 1.5:  # Wide rectangles
                        text_fields.append({
                            'position': (x + w//2, y + h//2),
                            'bounds': (x, y, w, h),
                            'area': area
                        })
            
            return text_fields
        except Exception as e:
            print(f"Fast text field detection failed: {e}")
            return []

    def find_clickable_elements_fast(self, cv_image):
        """Faster clickable element detection"""
        try:
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Simplified contour detection
            contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            clickable_elements = []
            for contour in contours[:15]:  # Limit for performance
                area = cv2.contourArea(contour)
                if 50 < area < 8000:
                    x, y, w, h = cv2.boundingRect(contour)
                    clickable_elements.append({
                        'position': (x + w//2, y + h//2),
                        'bounds': (x, y, w, h),
                        'area': area
                    })
            
            return clickable_elements
        except Exception as e:
            print(f"Fast clickable detection failed: {e}")
            return []


  
    
    def extract_all_text(self, screenshot):
        """Extract all text from screen using multiple OCR methods"""
        try:
            # Method 1: Tesseract
            tesseract_text = pytesseract.image_to_string(screenshot)
        except Exception as e:
            print(f"Tesseract OCR failed: {e}")
            tesseract_text = ""
        
        try:
            # Method 2: EasyOCR (better for various fonts)
            easyocr_results = self.ocr_reader.readtext(np.array(screenshot))
            easyocr_text = ' '.join([result[1] for result in easyocr_results])
        except Exception as e:
            print(f"EasyOCR failed: {e}")
            easyocr_text = ""
        
        # Combine and clean results
        all_text = f"{tesseract_text}\n{easyocr_text}"
        return self.clean_extracted_text(all_text)
    
    def clean_extracted_text(self, text):
        """Clean and normalize extracted text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        cleaned_text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might cause issues
        cleaned_text = re.sub(r'[^\w\s\-.,!?@#$%^&*()+=<>:;"\'/\\|`~]', '', cleaned_text)
        
        # Remove very short fragments (likely OCR noise)
        words = cleaned_text.split()
        meaningful_words = [word for word in words if len(word) > 1 or word.isalnum()]
        
        return ' '.join(meaningful_words).strip()
    
    def detect_ui_elements(self, cv_image):
        """Detect buttons, text fields, and other UI elements"""
        try:
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
        except Exception as e:
            print(f"UI element detection failed: {e}")
            return {'buttons': [], 'text_fields': [], 'images': []}
    
    def find_buttons(self, gray_image):
        """Find button-like elements"""
        try:
            # Use edge detection to find rectangular shapes
            edges = cv2.Canny(gray_image, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            buttons = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if 500 < area < 5000:  # Button-sized areas
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h
                    if 0.5 < aspect_ratio < 4:  # Reasonable button proportions
                        buttons.append({
                            'position': (x + w//2, y + h//2),
                            'bounds': (x, y, w, h),
                            'area': area
                        })
            
            return buttons
        except Exception as e:
            print(f"Button detection failed: {e}")
            return []
    
    def find_text_fields(self, gray_image):
        """Find text input fields"""
        try:
            # Look for rectangular areas that might be text fields
            edges = cv2.Canny(gray_image, 30, 100)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            text_fields = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if 1000 < area < 10000:  # Text field sized areas
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h
                    if aspect_ratio > 2:  # Wide rectangles (typical for text fields)
                        text_fields.append({
                            'position': (x + w//2, y + h//2),
                            'bounds': (x, y, w, h),
                            'area': area
                        })
            
            return text_fields
        except Exception as e:
            print(f"Text field detection failed: {e}")
            return []
    
    def find_images(self, cv_image):
        """Find image elements on screen"""
        try:
            # Simple image detection based on color variance
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Find areas with high variance (likely images)
            kernel = np.ones((5,5), np.uint8)
            variance = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # This is a simplified approach - in practice, you'd use more sophisticated methods
            return []
        except Exception as e:
            print(f"Image detection failed: {e}")
            return []
    
    def find_clickable_elements(self, cv_image):
        """Find all clickable elements on screen"""
        try:
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
        except Exception as e:
            print(f"Clickable element detection failed: {e}")
            return []
    
    def analyze_screen_layout(self, cv_image):
        """Analyze the overall screen layout"""
        try:
            height, width = cv_image.shape[:2]
            
            return {
                'screen_size': (width, height),
                'regions': {
                    'top': (0, 0, width, height//4),
                    'middle': (0, height//4, width, height//2),
                    'bottom': (0, 3*height//4, width, height//4)
                }
            }
        except Exception as e:
            print(f"Screen layout analysis failed: {e}")
            return {'screen_size': (0, 0), 'regions': {}}
    
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
        except Exception as e:
            print(f"Application identification failed: {e}")
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
