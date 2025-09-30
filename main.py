import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import random
from datetime import datetime
import json
import os


class FallingLeaf:
    def __init__(self, canvas, canvas_width):
        self.canvas = canvas
        self.canvas_width = canvas_width
        self.size = random.randint(15, 30)
        self.speed = random.uniform(1, 3)
        # Start from random position across full width
        self.x = random.randint(0, canvas_width)
        self.y = -self.size
        self.rotation = 0
        self.rotation_speed = random.uniform(-5, 5)
        self.wind_effect = random.uniform(-0.5, 0.5)

        # Autumn colors palette
        self.colors = ['#FF6B35', '#F7934C', '#FFA62B', '#E57A44', '#D36E70',
                       '#8C5E35', '#A63C3C', '#BF5E3C', '#E68A2E', '#D4A76A']
        self.color = random.choice(self.colors)

        # Different leaf shapes for variety
        self.leaf_type = random.choice(['oval', 'maple', 'simple'])

        if self.leaf_type == 'oval':
            self.leaf = self.canvas.create_oval(
                self.x, self.y, self.x + self.size, self.y + self.size,
                fill=self.color, outline='', width=0
            )
        elif self.leaf_type == 'maple':
            # Simplified maple leaf shape
            points = [
                self.x + self.size / 2, self.y,
                self.x + self.size, self.y + self.size / 3,
                self.x + self.size * 0.8, self.y + self.size / 2,
                self.x + self.size, self.y + self.size * 0.7,
                self.x + self.size * 0.7, self.y + self.size,
                self.x + self.size / 2, self.y + self.size * 0.8,
                self.x + self.size * 0.3, self.y + self.size,
                self.x, self.y + self.size * 0.7,
                self.x + self.size * 0.2, self.y + self.size / 2,
                self.x, self.y + self.size / 3
            ]
            self.leaf = self.canvas.create_polygon(points, fill=self.color, outline='', smooth=True)
        else:
            # Simple pointed leaf
            points = [
                self.x + self.size / 2, self.y,
                self.x + self.size, self.y + self.size / 3,
                self.x + self.size * 0.6, self.y + self.size,
                self.x + self.size / 2, self.y + self.size * 0.7,
                self.x + self.size * 0.4, self.y + self.size
            ]
            self.leaf = self.canvas.create_polygon(points, fill=self.color, outline='', smooth=True)

        # Leaf stem
        self.stem = self.canvas.create_line(
            self.x + self.size / 2, self.y + self.size,
            self.x + self.size / 2, self.y + self.size + 5,
            fill=self.color, width=1
        )

    def update(self):
        self.y += self.speed
        self.x += self.wind_effect + random.uniform(-0.5, 0.5)
        self.rotation += self.rotation_speed

        # Apply movement based on leaf type
        if self.leaf_type == 'oval':
            self.canvas.coords(self.leaf,
                               self.x, self.y,
                               self.x + self.size, self.y + self.size)
        else:
            # For polygons, use move for simplicity
            self.canvas.move(self.leaf, self.wind_effect + random.uniform(-0.3, 0.3), self.speed)
            self.canvas.move(self.stem, self.wind_effect + random.uniform(-0.3, 0.3), self.speed)

        # Update stem position
        self.canvas.coords(self.stem,
                           self.x + self.size / 2, self.y + self.size,
                           self.x + self.size / 2 + random.uniform(-1, 1),
                           self.y + self.size + 5)

        # Remove leaf if it falls below the screen
        if self.y > 600:
            self.canvas.delete(self.leaf)
            self.canvas.delete(self.stem)
            return False
        return True


class SeptemberNotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🍂 September Notes - Autumn Vibes 🍂")
        self.root.geometry("1000x700")  # Wider window for full-width leaves
        self.root.configure(bg='#8B4513')

        # Application settings
        self.settings_file = "september_settings.json"
        self.notes_dir = "september_notes"

        # Current theme settings
        self.themes = {
            "Classic Autumn": {"bg": "#8B4513", "frame": "#D2691E", "text_bg": "#FFF8DC"},
            "Golden Autumn": {"bg": "#D4A017", "frame": "#B8860B", "text_bg": "#FAF0E6"},
            "Late Autumn": {"bg": "#556B2F", "frame": "#6B8E23", "text_bg": "#F5F5DC"},
            "Crimson Autumn": {"bg": "#8B0000", "frame": "#A52A2A", "text_bg": "#FFE4E1"}
        }

        # Initialize settings first
        self.load_settings()
        self.create_notes_directory()

        # Create widget styles
        self.style = ttk.Style()
        self.set_theme(self.current_theme)

        # Main frame
        main_frame = ttk.Frame(root, style='Autumn.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Top panel with date, time and settings
        top_frame = ttk.Frame(main_frame, style='Autumn.TFrame')
        top_frame.pack(fill=tk.X, pady=(0, 10))

        # Date label
        self.date_label = ttk.Label(top_frame,
                                    text=self.get_current_date(),
                                    style='Autumn.TLabel',
                                    font=('Arial', 14, 'bold'))
        self.date_label.pack(side=tk.LEFT)

        # Time label
        self.time_label = ttk.Label(top_frame,
                                    text=self.get_current_time(),
                                    style='Autumn.TLabel',
                                    font=('Arial', 14, 'bold'))
        self.time_label.pack(side=tk.RIGHT)

        # Settings button
        settings_btn = ttk.Button(top_frame, text="🎨 Settings",
                                  command=self.show_settings)
        settings_btn.pack(side=tk.RIGHT, padx=(0, 10))

        # Main content container
        content_frame = ttk.Frame(main_frame, style='Autumn.TFrame')
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas for falling leaves (full width)
        self.canvas = tk.Canvas(content_frame,
                                bg=self.themes[self.current_theme]["bg"],
                                highlightthickness=0,
                                width=600)  # Wider canvas for full-width leaves
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Right side with notes
        right_frame = ttk.Frame(content_frame, style='Autumn.TFrame')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Notes header and management
        notes_header = ttk.Frame(right_frame, style='Autumn.TFrame')
        notes_header.pack(fill=tk.X, pady=(0, 10))

        notes_label = ttk.Label(notes_header,
                                text="🍁 Autumn Thoughts:",
                                style='Autumn.TLabel',
                                font=('Arial', 16, 'bold'))
        notes_label.pack(side=tk.LEFT)

        # Existing notes selection
        self.notes_combobox = ttk.Combobox(notes_header,
                                           values=self.get_saved_notes(),
                                           state="readonly",
                                           width=20)
        self.notes_combobox.pack(side=tk.RIGHT, padx=(5, 0))
        self.notes_combobox.bind('<<ComboboxSelected>>', self.load_selected_note)

        # Text area with scrollbar
        self.text_area = scrolledtext.ScrolledText(
            right_frame,
            wrap=tk.WORD,
            width=40,
            height=20,
            font=('Arial', 12),
            bg=self.themes[self.current_theme]["text_bg"],
            fg='#8B4513',
            relief=tk.FLAT,
            padx=15,
            pady=15,
            insertbackground='#8B4513'  # Cursor color
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to work...")
        status_bar = ttk.Label(right_frame, textvariable=self.status_var,
                               style='Autumn.TLabel', relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, pady=(10, 0))

        # Control buttons
        button_frame = ttk.Frame(right_frame, style='Autumn.TFrame')
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(button_frame,
                   text="💾 Save Note",
                   command=self.save_note).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(button_frame,
                   text="🆕 New Note",
                   command=self.new_note).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(button_frame,
                   text="🗑️ Delete Note",
                   command=self.delete_note).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(button_frame,
                   text="❌ Clear",
                   command=self.clear_notes).pack(side=tk.LEFT)

        # Active leaves list
        self.leaves = []
        self.leaf_density = 1.0  # Leaf density

        # Start animations
        self.animate_leaves()
        self.update_datetime()

        # Create initial leaves
        for _ in range(20):
            self.create_leaf()

    def set_theme(self, theme_name):
        """Apply the selected theme to the application"""
        self.current_theme = theme_name
        theme = self.themes[theme_name]
        self.style.configure('Autumn.TFrame', background=theme["frame"])
        self.style.configure('Autumn.TLabel',
                             background=theme["frame"],
                             foreground='white',
                             font=('Arial', 12))

    def create_notes_directory(self):
        """Create notes directory if it doesn't exist"""
        if not os.path.exists(self.notes_dir):
            os.makedirs(self.notes_dir)

    def load_settings(self):
        """Load application settings from JSON file with error handling"""
        try:
            # If settings file exists, try to load it
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.current_theme = settings.get('theme', 'Classic Autumn')
                    self.leaf_density = settings.get('leaf_density', 1.0)

                    # Validate that the theme exists
                    if self.current_theme not in self.themes:
                        self.current_theme = 'Classic Autumn'
            else:
                # Use default settings if file doesn't exist
                self.current_theme = 'Classic Autumn'
                self.leaf_density = 1.0

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # If there's an error reading the file, use defaults and recreate it
            print(f"Error loading settings: {e}. Using default settings.")
            self.current_theme = 'Classic Autumn'
            self.leaf_density = 1.0
            self.save_settings()  # This will create a new settings file

    def save_settings(self):
        """Save application settings to JSON file"""
        settings = {
            'theme': self.current_theme,
            'leaf_density': self.leaf_density
        }
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get_saved_notes(self):
        """Get list of all saved notes"""
        try:
            notes = [f for f in os.listdir(self.notes_dir) if f.endswith('.txt')]
            return sorted(notes, reverse=True)
        except FileNotFoundError:
            return []

    def load_selected_note(self, event):
        """Load the selected note from combobox"""
        selected_note = self.notes_combobox.get()
        if selected_note:
            try:
                with open(os.path.join(self.notes_dir, selected_note), 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.text_area.delete("1.0", tk.END)
                    self.text_area.insert("1.0", content)
                self.status_var.set(f"Note '{selected_note}' loaded")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load note: {str(e)}")

    def delete_note(self):
        """Delete the currently selected note"""
        selected_note = self.notes_combobox.get()
        if not selected_note:
            messagebox.showwarning("Warning", "No note selected for deletion")
            return

        if messagebox.askyesno("Confirm Deletion",
                               f"Are you sure you want to delete '{selected_note}'?"):
            try:
                file_path = os.path.join(self.notes_dir, selected_note)
                os.remove(file_path)

                # Update combobox
                self.notes_combobox.set('')
                self.notes_combobox['values'] = self.get_saved_notes()

                # Clear text area if the deleted note was loaded
                current_content = self.text_area.get("1.0", tk.END).strip()
                if current_content:
                    # Check if current content matches the deleted file
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            # If we get here, file still exists (shouldn't happen)
                            pass
                    except FileNotFoundError:
                        # File is deleted, clear the text area
                        self.text_area.delete("1.0", tk.END)

                self.status_var.set(f"Note '{selected_note}' deleted")
                messagebox.showinfo("Success", "Note deleted successfully")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete note: {str(e)}")

    def show_settings(self):
        """Show settings window for customization"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Autumn Atmosphere Settings")
        settings_window.geometry("400x300")
        settings_window.configure(bg=self.themes[self.current_theme]["frame"])
        settings_window.transient(self.root)
        settings_window.grab_set()

        ttk.Label(settings_window, text="Select theme:", style='Autumn.TLabel').pack(pady=10)

        theme_var = tk.StringVar(value=self.current_theme)
        for theme_name in self.themes.keys():
            ttk.Radiobutton(settings_window, text=theme_name,
                            variable=theme_var, value=theme_name,
                            style='Autumn.TRadiobutton').pack(anchor=tk.W, padx=20)

        ttk.Label(settings_window, text="Leaf density:", style='Autumn.TLabel').pack(pady=10)

        density_var = tk.DoubleVar(value=self.leaf_density)
        density_scale = ttk.Scale(settings_window, from_=0.1, to=2.0,
                                  variable=density_var, orient=tk.HORIZONTAL)
        density_scale.pack(fill=tk.X, padx=20)

        def apply_settings():
            """Apply the selected settings"""
            self.current_theme = theme_var.get()
            self.leaf_density = density_var.get()
            self.set_theme(self.current_theme)
            self.canvas.configure(bg=self.themes[self.current_theme]["bg"])
            self.text_area.configure(bg=self.themes[self.current_theme]["text_bg"])
            self.save_settings()
            settings_window.destroy()
            self.status_var.set("Settings applied")

        ttk.Button(settings_window, text="Apply",
                   command=apply_settings).pack(pady=20)

    def create_leaf(self):
        """Create a new falling leaf"""
        # Get current canvas width for full-width leaf distribution
        canvas_width = 600  # Fixed width from our canvas setup
        leaf = FallingLeaf(self.canvas, canvas_width)
        self.leaves.append(leaf)

    def animate_leaves(self):
        """Animate all falling leaves"""
        active_leaves = []
        for leaf in self.leaves:
            if leaf.update():
                active_leaves.append(leaf)

        self.leaves = active_leaves

        # Create new leaves based on density setting
        if random.random() < 0.08 * self.leaf_density:
            self.create_leaf()

        self.root.after(50, self.animate_leaves)

    def get_current_date(self):
        """Get formatted current date"""
        now = datetime.now()
        months_en = {
            1: 'January', 2: 'February', 3: 'March', 4: 'April',
            5: 'May', 6: 'June', 7: 'July', 8: 'August',
            9: 'September', 10: 'October', 11: 'November', 12: 'December'
        }
        return f"📅 {now.day} {months_en[now.month]} {now.year}"

    def get_current_time(self):
        """Get formatted current time"""
        return f"⏰ {datetime.now().strftime('%H:%M:%S')}"

    def update_datetime(self):
        """Update date and time labels"""
        self.date_label.config(text=self.get_current_date())
        self.time_label.config(text=self.get_current_time())
        self.root.after(1000, self.update_datetime)

    def save_note(self):
        """Save current note to file"""
        note = self.text_area.get("1.0", tk.END).strip()
        if note:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"september_note_{timestamp}.txt"
            filepath = os.path.join(self.notes_dir, filename)

            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"Note from {self.get_current_date()} {self.get_current_time()}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(note)

                self.status_var.set(f"Note saved as {filename}")
                # Update notes list
                self.notes_combobox['values'] = self.get_saved_notes()

            except Exception as e:
                messagebox.showerror("Error", f"Failed to save note: {str(e)}")
        else:
            messagebox.showwarning("Warning", "Note is empty!")

    def new_note(self):
        """Create a new empty note"""
        self.text_area.delete("1.0", tk.END)
        self.notes_combobox.set('')
        self.status_var.set("New note created")

    def clear_notes(self):
        """Clear the current note"""
        if messagebox.askyesno("Confirmation", "Clear current note?"):
            self.text_area.delete("1.0", tk.END)
            self.status_var.set("Note cleared")


def main():
    """Main application entry point"""
    root = tk.Tk()

    # Try to set autumn icon (if available)
    try:
        root.iconbitmap("autumn_leaf.ico")  # You can add your own icon
    except:
        pass

    app = SeptemberNotesApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()