from PIL import Image
import numpy as np
import os
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk
from tkinter.colorchooser import askcolor
import webbrowser

# Extended ASCII character sets
ASCII_CHAR_SETS = {
    "Standard": ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."],
    "Detailed": ["$", "@", "B", "%", "8", "&", "W", "M", "#", "*", "o", "a", "h", "k", "b", "d", "p", "q", "w", "m", "Z", "O", "0", "Q", "L", "C", "J", "U", "Y", "X", "z", "c", "v", "u", "n", "x", "r", "j", "f", "t", "/", "\\", "|", "(", ")", "1", "{", "}", "[", "]", "?", "-", "_", "+", "~", "<", ">", "i", "!", "l", "I", ";", ":", ",", "\"", "^", "`", "'", ".", " "],
    "Simple": ["#", "&", "%", "?", "*", "+", "=", "-", ":", ".", " "],
    "Blocks": ["█", "▓", "▒", "░", "⣿", "⣷", "⣧", "⣶", "⣦", "⣤", "⣀", " "],
    "Shapes": ["■", "□", "▪", "▫", "◆", "◇", "●", "○", "★", "☆", " "],
    "Braille": ["⣿", "⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷", "⣶", "⣦", "⣤", "⣄", "⣀", "⡀", "⠄", "⠂", "⠁", "⠀"]
}

# Theme colors with improved button text contrast
THEMES = {
    "Dark": {
        "bg": "#121212",  # Darker background for modern look
        "fg": "#E0E0E0",  # Soft white for better readability
        "button": "#2D2D2D",  # Slightly lighter than bg
        "button_text": "#000000", 
        "highlight": "#BB86FC",  # Purple accent (Material Design)
        "text_bg": "#1E1E1E",  # Slightly lighter than bg
        "text_fg": "#FFFFFF"
    },
    "Light": {
        "bg": "#FAFAFA",  # Pure white is harsh, this is softer
        "fg": "#212121",  # Dark gray instead of pure black
        "button": "#E0E0E0",
        "button_text": "#000000",
        "highlight": "#6200EE",  # Material Design purple
        "text_bg": "#FFFFFF",
        "text_fg": "#212121"
    },
    "Blue": {
        "bg": "#0D1B2A",  # Deep navy
        "fg": "#E0E1DD",  # Off-white
        "button": "#1B263B",
        "button_text": "#0D1B2A",
        "highlight": "#415A77",  # Medium blue
        "text_bg": "#1B263B",
        "text_fg": "#E0E1DD"
    },
    "Green": {
        "bg": "#1B3B28",  # Deep forest green
        "fg": "#E8F5E9",  # Light greenish white
        "button": "#2E4E3A",
        "button_text": "#1B3B28",
        "highlight": "#4CAF50",  # Keeping your original green
        "text_bg": "#2E4E3A",
        "text_fg": "#E8F5E9"
    },
    "Purple": {
        "bg": "#1A1A2E",  # Deep purple-dark
        "fg": "#E6E6FA",  # Lavender white
        "button": "#2A2A3A",
        "button_text": "#1A1A2E",
        "highlight": "#9575CD",  # Softer purple
        "text_bg": "#2A2A3A",
        "text_fg": "#E6E6FA"
    }
}
def grayscale(img):
    return img.convert("L")

def resize_image(img, new_width=100):
    width, height = img.size
    ratio = height / width
    new_height = int(new_width * ratio)
    return img.resize((new_width, new_height))

def pixel_to_ascii(pixel, char_set):
    # Scalable mapping
    index = int(pixel / 255 * (len(char_set) - 1))
    return char_set[index]

def image_to_ascii(image_path, new_width=100, char_set=None, invert=False):
    if char_set is None:
        char_set = ASCII_CHAR_SETS["Standard"]
    
    # Inversion option
    if invert:
        char_set = char_set[::-1]
        
    try:
        img = Image.open(image_path)
        img = resize_image(img, new_width)
        img = grayscale(img)
        pixels = np.array(img)
        ascii_str = ""
        for row in pixels:
            for pixel in row:
                ascii_str += pixel_to_ascii(pixel, char_set)
            ascii_str += "\n"
        return ascii_str
    except Exception as e:
        print(f"Error: {e}")
        return None

class ASCIIArtConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("ASCII Art Converter")
        self.root.geometry("900x700")
        
        # Default theme
        self.current_theme = "Dark"
        self.apply_theme(THEMES[self.current_theme])
        
        # Main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Style configuration
        self.style = ttk.Style()
        self.configure_styles()
        
        # Top section (settings)
        self.settings_frame = ttk.LabelFrame(self.main_frame, text="Settings", padding="10")
        self.settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Top layout
        self.top_frame = ttk.Frame(self.settings_frame)
        self.top_frame.pack(fill=tk.X)
        
        # Image selection button
        self.select_button = ttk.Button(self.top_frame, text="Select Image", command=self.select_image, style="Accent.TButton")
        self.select_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Selected filename
        self.file_label = ttk.Label(self.top_frame, text="No file selected yet")
        self.file_label.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        
        # Settings section
        self.options_frame = ttk.Frame(self.settings_frame)
        self.options_frame.pack(fill=tk.X, pady=5)
        
        # Width setting
        self.width_frame = ttk.Frame(self.options_frame)
        self.width_frame.pack(side=tk.LEFT, padx=5)
        
        self.width_label = ttk.Label(self.width_frame, text="ASCII width:")
        self.width_label.pack(side=tk.LEFT, padx=5)
        
        self.width_var = tk.StringVar(value="100")
        self.width_entry = ttk.Entry(self.width_frame, textvariable=self.width_var, width=5)
        self.width_entry.pack(side=tk.LEFT)
        
        # Character set selection
        self.charset_frame = ttk.Frame(self.options_frame)
        self.charset_frame.pack(side=tk.LEFT, padx=20)
        
        self.charset_label = ttk.Label(self.charset_frame, text="Character Set:")
        self.charset_label.pack(side=tk.LEFT, padx=5)
        
        self.charset_var = tk.StringVar(value="Standard")
        self.charset_combo = ttk.Combobox(self.charset_frame, textvariable=self.charset_var, 
                                         values=list(ASCII_CHAR_SETS.keys()), width=10)
        self.charset_combo.pack(side=tk.LEFT)
        
        # Inversion option
        self.invert_var = tk.BooleanVar(value=False)
        self.invert_check = ttk.Checkbutton(self.options_frame, text="Invert Colors", 
                                           variable=self.invert_var)
        self.invert_check.pack(side=tk.LEFT, padx=10)
        
        # Convert button
        self.convert_button = ttk.Button(self.settings_frame, text="Convert", 
                                        command=self.convert_image, style="Accent.TButton")
        self.convert_button.pack(pady=10)
        
        # Middle section (result)
        self.result_frame = ttk.LabelFrame(self.main_frame, text="ASCII Art", padding="10")
        self.result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Font setting
        self.font_frame = ttk.Frame(self.result_frame)
        self.font_frame.pack(fill=tk.X, pady=5)
        
        self.font_label = ttk.Label(self.font_frame, text="Font Size:")
        self.font_label.pack(side=tk.LEFT, padx=5)
        
        self.font_size_var = tk.StringVar(value="10")
        self.font_size_combo = ttk.Combobox(self.font_frame, textvariable=self.font_size_var, 
                                           values=["6", "8", "10", "12", "14"], width=5)
        self.font_size_combo.pack(side=tk.LEFT)
        self.font_size_combo.bind("<<ComboboxSelected>>", self.update_font)
        
        # Theme selection
        self.theme_frame = ttk.Frame(self.font_frame)
        self.theme_frame.pack(side=tk.RIGHT, padx=5)
        
        self.theme_label = ttk.Label(self.theme_frame, text="Theme:")
        self.theme_label.pack(side=tk.LEFT, padx=5)
        
        self.theme_var = tk.StringVar(value=self.current_theme)
        self.theme_combo = ttk.Combobox(self.theme_frame, textvariable=self.theme_var, 
                                       values=list(THEMES.keys()), width=10)
        self.theme_combo.pack(side=tk.LEFT)
        self.theme_combo.bind("<<ComboboxSelected>>", self.change_theme)
        
        # ASCII art display area
        self.result_text = scrolledtext.ScrolledText(self.result_frame, font=("Courier", 10))
        self.result_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Bottom section (buttons)
        self.buttons_frame = ttk.Frame(self.main_frame)
        self.buttons_frame.pack(fill=tk.X, pady=10)
        
        # Save button
        self.save_button = ttk.Button(self.buttons_frame, text="Save ASCII File", 
                                     command=self.save_ascii, style="Accent.TButton")
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        # Copy button
        self.copy_button = ttk.Button(self.buttons_frame, text="Copy to Clipboard", 
                                     command=self.copy_to_clipboard)
        self.copy_button.pack(side=tk.LEFT, padx=5)
        
        # Clear button
        self.clear_button = ttk.Button(self.buttons_frame, text="Clear", 
                                      command=self.clear_result)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # Info button
        self.info_button = ttk.Button(self.buttons_frame, text="About", 
                                     command=self.show_about)
        self.info_button.pack(side=tk.RIGHT, padx=5)
        
        # Initial state
        self.image_path = None
        self.ascii_result = None
        
        # Disable buttons initially
        self.save_button.config(state=tk.DISABLED)
        self.copy_button.config(state=tk.DISABLED)
        self.clear_button.config(state=tk.DISABLED)

    def configure_styles(self):
        # Configure TTK styles
        theme = THEMES[self.current_theme]
        bg_color = theme["bg"]
        fg_color = theme["fg"]
        button_color = theme["button"]
        button_text = theme["button_text"]
        highlight = theme["highlight"]
        text_bg = theme["text_bg"]
        text_fg = theme["text_fg"]
        
        self.style.configure("TFrame", background=bg_color)
        self.style.configure("TLabel", background=bg_color, foreground=fg_color)
        self.style.configure("TButton", background=button_color, foreground=button_text)
        self.style.configure("Accent.TButton", background=highlight, foreground=button_text)
        self.style.configure("TCheckbutton", background=bg_color, foreground=fg_color)
        self.style.configure("TLabelframe", background=bg_color, foreground=fg_color)
        self.style.configure("TLabelframe.Label", background=bg_color, foreground=fg_color)
        
        # Combobox and Entry styles
        self.style.configure("TCombobox", fieldbackground=button_color, foreground=button_text)
        self.style.configure("TEntry", fieldbackground=button_color, foreground=button_text)
        
        # Text widget colors
        if hasattr(self, 'result_text'):
            self.result_text.config(bg=text_bg, fg=text_fg, insertbackground=text_fg)
        
        # Root background color
        self.root.config(bg=bg_color)

    def apply_theme(self, theme_dict):
        bg_color = theme_dict["bg"]
        fg_color = theme_dict["fg"]
        
        # Set colors for root and all widgets
        for widget in [self.root]:
            if isinstance(widget, tk.Tk) or isinstance(widget, tk.Frame):
                widget.config(bg=bg_color)
        
        # Text area colors
        if hasattr(self, 'result_text'):
            self.result_text.config(bg=theme_dict["text_bg"], fg=theme_dict["text_fg"], insertbackground=theme_dict["text_fg"])

    def change_theme(self, event=None):
        self.current_theme = self.theme_var.get()
        self.apply_theme(THEMES[self.current_theme])
        self.configure_styles()

    def update_font(self, event=None):
        size = int(self.font_size_var.get())
        self.result_text.config(font=("Courier", size))

    def select_image(self):
        self.image_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )
        if self.image_path:
            filename = os.path.basename(self.image_path)
            self.file_label.config(text=f"Selected: {filename}")

    def convert_image(self):
        if not self.image_path:
            messagebox.showerror("Error", "Please select an image first.")
            return
        
        try:
            width = int(self.width_var.get())
            if width <= 0:
                messagebox.showerror("Error", "Width must be a positive number.")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid width value.")
            return
        
        char_set = ASCII_CHAR_SETS[self.charset_var.get()]
        invert = self.invert_var.get()
        
        self.ascii_result = image_to_ascii(self.image_path, width, char_set, invert)
        
        if self.ascii_result:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, self.ascii_result)
            
            # Enable buttons
            self.save_button.config(state=tk.NORMAL)
            self.copy_button.config(state=tk.NORMAL)
            self.clear_button.config(state=tk.NORMAL)
        else:
            messagebox.showerror("Error", "An error occurred during ASCII conversion.")

    def save_ascii(self):
        if not self.ascii_result:
            messagebox.showerror("Error", "No ASCII art found to save.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save ASCII File",
            defaultextension=".txt",
            filetypes=[("Text File", "*.txt"), ("HTML File", "*.html")]
        )
        
        if file_path:
            try:
                # Save as HTML if .html extension
                if file_path.endswith('.html'):
                    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>ASCII Art</title>
    <style>
        body {{ background-color: {THEMES[self.current_theme]["bg"]}; color: {THEMES[self.current_theme]["fg"]}; }}
        pre {{ font-family: Courier, monospace; line-height: 0.8; }}
    </style>
</head>
<body>
    <pre>{self.ascii_result}</pre>
</body>
</html>
"""
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                else:
                    # Save as normal text file
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(self.ascii_result)
                messagebox.showinfo("Success", f"ASCII art saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error saving file: {e}")

    def copy_to_clipboard(self):
        if not self.ascii_result:
            messagebox.showerror("Error", "No ASCII art found to copy.")
            return
            
        self.root.clipboard_clear()
        self.root.clipboard_append(self.ascii_result)
        messagebox.showinfo("Success", "ASCII art copied to clipboard.")

    def clear_result(self):
        self.result_text.delete(1.0, tk.END)
        self.ascii_result = None
        self.save_button.config(state=tk.DISABLED)
        self.copy_button.config(state=tk.DISABLED)
        self.clear_button.config(state=tk.DISABLED)

    def show_about(self):
        about_text = """ASCII Art Converter v2.0
        
This program converts images to ASCII art.

Features:
- Multiple character sets
- Theme support
- Adjustable width and font size
- Save and copy functions

How to use:
1. Click "Select Image" to choose an image file
2. Adjust settings as desired
3. Click "Convert" button
4. Save or copy the result

Enhancements:
- Improved theme contrast for buttons
- Added separate text background/foreground colors
- Support for HTML export
- More character sets
"""
        messagebox.showinfo("About", about_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = ASCIIArtConverter(root)
    root.mainloop()