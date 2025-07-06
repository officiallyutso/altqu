import tkinter as tk
from tkinter import ttk

class ChatInterface:
    def __init__(self, ai_engine, executor):
        self.ai_engine = ai_engine
        self.executor = executor
        self.setup_ui()
        
    def setup_ui(self):
        self.root = tk.Tk()
        self.root.title("AI Assistant")
        self.root.geometry("400x100")
        self.root.attributes('-topmost', True)
        
        # Input field
        self.input_var = tk.StringVar()
        self.input_field = ttk.Entry(
            self.root, 
            textvariable=self.input_var,
            font=('Arial', 12)
        )
        self.input_field.pack(fill='x', padx=10, pady=10)
        self.input_field.bind('<Return>', self.process_input)
        self.input_field.focus()
        
    def process_input(self, event):
        user_input = self.input_var.get()
        if user_input.strip():
            # Process with AI engine
            parsed_command = self.ai_engine.process_command(user_input)
            self.executor.execute_command(parsed_command)
            self.hide_interface()
            
    def show_interface(self):
        self.root.deiconify()
        self.input_field.focus()
        
    def hide_interface(self):
        self.input_var.set("")
        self.root.withdraw()
