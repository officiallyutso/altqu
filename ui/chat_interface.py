import tkinter as tk
from tkinter import ttk
import threading

class ChatInterface:
    def __init__(self, ai_engine, executor, context_manager, root=None, screen_intelligence=None):
        self.ai_engine = ai_engine
        self.executor = executor
        self.context_manager = context_manager
        self.screen_intelligence = screen_intelligence
        self.current_screen_analysis = None
        
        # Use provided root or create new one
        if root:
            self.root = root
            self.setup_ui()
        else:
            self.root = tk.Tk()
            self.setup_ui()
            self.root.withdraw()
        
    def setup_ui(self):
        # Create a toplevel window for the chat interface
        self.chat_window = tk.Toplevel(self.root)
        self.chat_window.title("AI Assistant")
        self.chat_window.geometry("500x120")
        self.chat_window.attributes('-topmost', True)
        self.chat_window.configure(bg='#2b2b2b')
        self.chat_window.protocol("WM_DELETE_WINDOW", self.hide_interface)
        
        
        # Create main frame
        main_frame = tk.Frame(self.chat_window, bg='#2b2b2b')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Status label
        self.status_label = tk.Label(
            main_frame, 
            text="AI Assistant Ready - Type your command...",
            bg='#2b2b2b',
            fg='#ffffff',
            font=('Arial', 10)
        )
        self.status_label.pack(pady=(0, 5))
        
        # Input field
        self.input_var = tk.StringVar()
        self.input_field = ttk.Entry(
            main_frame,
            textvariable=self.input_var,
            font=('Arial', 12),
            width=60
        )
        self.input_field.pack(fill='x', pady=5)
        self.input_field.bind('<Return>', self.process_input)
        self.input_field.bind('<Escape>', lambda e: self.hide_interface())
        self.input_field.bind('<Control-w>', lambda e: self.hide_interface())  # Ctrl+W to close
        self.input_field.bind('<Control-Return>', lambda e: self.process_input(e))  # Ctrl+Enter to execute
        
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg='#2b2b2b')
        button_frame.pack(fill='x', pady=5)
        
        # Send button
        self.send_button = tk.Button(
            button_frame,
            text="Execute",
            command=lambda: self.process_input(None),
            bg='#4CAF50',
            fg='white',
            font=('Arial', 10),
            relief='flat'
        )
        self.send_button.pack(side='right', padx=(5, 0))
        
        # Cancel button
        self.cancel_button = tk.Button(
            button_frame,
            text="Cancel",
            command=self.hide_interface,
            bg='#f44336',
            fg='white',
            font=('Arial', 10),
            relief='flat'
        )
        self.cancel_button.pack(side='right')
        
        # Hide initially
        self.chat_window.withdraw()
        
    def process_input(self, event):
        user_input = self.input_var.get().strip()
        if not user_input:
            return
            
        # Update status
        self.status_label.config(text="Processing command...")
        self.chat_window.update()
        
        # Process in separate thread to avoid blocking UI
        threading.Thread(target=self._execute_command, args=(user_input,), daemon=True).start()
        
        
    
    def set_current_screen_analysis(self, screen_analysis):
        """Set the current screen analysis with progressive updates"""
        self.current_screen_analysis = screen_analysis
        
        if screen_analysis:
            app_name = screen_analysis.get('current_app', {}).get('app_name', 'Unknown')
            text_length = len(screen_analysis.get('text_content', ''))
            ui_elements = len(screen_analysis.get('clickable_areas', []))
            
            status_text = f"✓ Screen analyzed: {app_name} | {text_length} chars | {ui_elements} elements"
        else:
            status_text = "⚠ Screen analysis in progress..."
        
        if hasattr(self, 'status_label'):
            self.status_label.config(text=status_text)
        
    
    def _execute_command(self, user_input):
        try:
            # Use intelligent processing
            parsed_command = self.ai_engine.process_intelligent_command(
                user_input, 
                self.current_screen_analysis
            )
            
            # Execute with intelligence
            self.executor.execute_intelligent_command(
                parsed_command, 
                self.current_screen_analysis
            )
            
            # Save interaction
            self.context_manager.save_interaction(
                user_input,
                str(parsed_command),
                self.current_screen_analysis
            )
            
            self.root.after(0, self._command_completed, "Intelligent command executed!")
            
        except Exception as e:
            self.root.after(0, self._command_completed, f"Error: {str(e)}")
            
    def _command_completed(self, message):
        self.status_label.config(text=message)
        # self.root.after(2000, self.hide_interface)  # Hide after 2 seconds
        
    def show_interface(self):
        """Show the chat interface immediately"""
        self.chat_window.deiconify()
        self.chat_window.lift()
        self.chat_window.focus_force()
        self.input_field.focus()
        # Show immediate status while analysis runs in background
        self.status_label.config(text="🔍 Analyzing screen... Ready for commands!")
        
    def hide_interface(self):
        """Hide the chat interface"""
        self.input_var.set("")
        self.chat_window.withdraw()
