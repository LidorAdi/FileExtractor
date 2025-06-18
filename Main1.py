import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
from ttkthemes import ThemedTk
import os
import shutil
import pyperclip
import zipfile
import tarfile
import gzip
import sys,os
import datetime
import json

settings = {
    "source_dir": "",
    "output_dir": "",
    "processed_dir": ""
}

def save_settings(settings):
    base_dir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
    settings_path = os.path.join(base_dir, "settings.json")
    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=4)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)
def load_settings():
    default_settings = {
        "source_dir": "",
        "output_dir": "",
        "processed_dir": "",
        "theme": "arc"  # Added theme to default settings
    }

    settings_path = os.path.join(os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__), "settings.json")

    if os.path.exists(settings_path):
        try:
            with open(settings_path, "r") as f:
                settings = json.load(f)
                if 'theme' not in settings:  # Ensure theme exists
                    settings['theme'] = default_settings['theme']
                return settings
        except:
            pass  # corrupted or invalid JSON

    # If file doesn't exist or is invalid, create it
    with open(settings_path, "w") as f:
        json.dump(default_settings, f, indent=4)

    return default_settings
class FileExtractorApp:
    def __init__(self, master, settings):  # Added settings parameter
        self.master = master
        # Define theme bg colors early
        self.light_theme = 'arc'
        self.dark_theme = 'equilux' # Or another chosen dark theme
        self.light_bg_color = '#F0F0F0'
        self.dark_bg_color = '#2E2E2E'

        # Apply initial background color based on loaded theme
        # Ensure settings are loaded before this
        self.settings = settings
        current_theme = self.settings.get('theme', self.light_theme)
        if current_theme == self.light_theme:
            master.configure(background=self.light_bg_color)
        else:
            master.configure(background=self.dark_bg_color)

        master.title("File Extractor")
        master.geometry('950x700')
        icon_path = resource_path('resources/icon.ico')
        master.iconbitmap(icon_path)
        # Load settings FIRST (self.settings is already set above)

        # Top frame for buttons
        top_button_frame = ttk.Frame(master)
        top_button_frame.pack(anchor='w', padx=10, pady=(10, 0), fill='x')

        options_button = ttk.Button(top_button_frame, text="Edit Paths", command=self.open_options_window)
        options_button.pack(side='left', anchor='w')

        self.theme_toggle_button = ttk.Button(top_button_frame, text="Toggle Theme", command=self.toggle_theme)
        self.theme_toggle_button.pack(side='left', anchor='w', padx=(5,0))

        # Title label centered below the button
        title_label = ttk.Label(master, text="Service Request", font=("Arial", 18, "bold"))
        title_label.pack(pady=(5, 15))

        source_dir = self.settings.get("source_dir", "")
        if not source_dir or not os.path.exists(source_dir):
            self.files = []
        else:
            self.files = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f))]

        self.file_vars = {}


        self.folder_name_var = tk.StringVar()
        self.folder_name_entry = ttk.Entry(master, width=30, textvariable=self.folder_name_var , font=("Arial", 16))
        self.folder_name_entry.focus()
        self.folder_name_entry.selection_range(0, tk.END)
        self.folder_name_entry.pack(padx=20)
        clipboard_text = pyperclip.paste()
        if "6-000" in clipboard_text:
            self.folder_name_var.set(clipboard_text)
            self.folder_name_entry.focus()
            self.folder_name_entry.selection_range(0, tk.END)
        self.label = ttk.Label(master, text="Select Files:", font=("Arial", 12))
        self.label.pack(pady=10, padx=20)

        # Create Treeview with organized columns
        columns = ('name', 'date', 'size', 'type')
        self.tree = ttk.Treeview(master, columns=columns, show='headings', selectmode='none')
        self.tree.pack(fill='x', padx=10, pady=(5, 10))
        self.tree.bind("<Button-1>", self.on_treeview_click)

        # Column headers
        self.tree.heading('name', text='File Name')
        self.tree.heading('date', text='Date Modified')
        self.tree.heading('size', text='Size')
        self.tree.heading('type', text='Type')

        # Column widths and alignment
        self.tree.column('name', width=300, anchor='w')
        self.tree.column('date', width=140, anchor='center')
        self.tree.column('size', width=100, anchor='center')
        self.tree.column('type', width=60, anchor='center')

        # Populate the tree with file data
        for file in self.files:
            file_path = os.path.join(self.settings["source_dir"], file)

            modified_time = os.path.getmtime(file_path)
            formatted_date = datetime.datetime.fromtimestamp(modified_time).strftime('%Y-%m-%d %H:%M')

            file_type = os.path.splitext(file)[1].lstrip('.').upper() or 'NONE'

            file_size_bytes = os.path.getsize(file_path)
            if file_size_bytes >= 1024 ** 3:
                file_size = f"{file_size_bytes / (1024 ** 3):.2f} GB"
            else:
                file_size = f"{file_size_bytes / (1024 ** 2):.2f} MB"

            self.tree.insert('', 'end', values=(file, formatted_date, file_size, file_type))

        self.process_button = ttk.Button(master, text="Create Folder", command=self.process_files, style='Large.TButton')
        self.process_button.pack(pady=(15, 20))

        # Create a horizontal frame for both checkboxes
        options_frame = ttk.Frame(master)
        options_frame.pack(pady=5, padx=20)

        # Use date subfolder checkbox (left side)
        self.use_date_subfolder_var = tk.BooleanVar()
        self.use_date_subfolder_cb = ttk.Checkbutton(
            options_frame,
            text="Use today's date as subfolder",
            variable=self.use_date_subfolder_var
        )
        self.use_date_subfolder_cb.pack(side='left', padx=10)

        # Extract files checkbox (right side)
        self.extract_files_var = tk.BooleanVar(value=True)
        self.extract_cb = ttk.Checkbutton(
            options_frame,
            text="Extract files",
            variable=self.extract_files_var
        )
        self.extract_cb.pack(side='left', padx=10)

        folder_name = self.folder_name_var.get()
        if self.use_date_subfolder_var.get():
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            folder_name = os.path.join(folder_name, today)

        destination_folder = os.path.join(self.settings["output_dir"], folder_name)
        master.bind('<Return>', lambda event: self.process_files())

        refresh_button = ttk.Button(master, text="Refresh", command=self.refresh_file_list)
        refresh_button.pack(pady=(5, 10), padx=20)

        footer = ttk.Label(master, text="Made by Lidor Adi", font=("Arial", 8), foreground="gray")
        footer.pack(side='bottom', pady=(5, 2))

    def toggle_theme(self):
        current_theme = self.settings.get('theme', self.light_theme)
        if current_theme == self.light_theme:
            new_theme = self.dark_theme
        else:
            new_theme = self.light_theme

        self.settings['theme'] = new_theme
        save_settings(self.settings)

        try:
            # Get the style object associated with the master window
            style = ttk.Style(self.master)
            style.theme_use(new_theme)

            if new_theme == self.light_theme:
                self.master.configure(background=self.light_bg_color)
            else:
                self.master.configure(background=self.dark_bg_color)

            # Forcing an update of the widgets might be necessary
            # to ensure all visual elements refresh with the new theme.
            self.master.update_idletasks()

            # Optionally, re-apply specific styles if some widgets don't update automatically.
            # (Keeping the previous style configurations commented out for now,
            # as theme_use should handle most of it)
            # style.configure('.', font=('Arial', 10))
            # ... (other style.configure lines) ...

            # If the theme change is successful, we might want to update the
            # theme toggle button text to reflect the current state, e.g.,
            # "Switch to Dark Theme" or "Switch to Light Theme".
            # For now, keeping it simple.

        except Exception as e:
            print(f"Error switching theme with style.theme_use(): {e}")
            # Fallback: Inform user a restart is needed if dynamic switch fails
            messagebox.showerror(
                "Theme Switch Info",
                f"Theme set to {new_theme}. Please restart the application for the theme to fully apply."
            )

    def open_options_window(self):
        win = tk.Toplevel(self.master)
        win.title("Edit Paths")
        win.geometry("600x250")
        icon_path = resource_path('resources/icon.ico')
        win.iconbitmap(icon_path)

        # Labels and Entry fields
        ttk.Label(win, text="Source Directory:").pack(anchor='w', padx=10, pady=(5, 0))
        source_entry = ttk.Entry(win, width=80)
        source_entry.pack(fill='x', expand=True, padx=10, pady=(0, 5))
        source_entry.insert(0, self.settings["source_dir"])

        ttk.Label(win, text="Output Directory:").pack(anchor='w', padx=10, pady=(5, 0))
        output_entry = ttk.Entry(win, width=80)
        output_entry.pack(fill='x', expand=True, padx=10, pady=(0, 5))
        output_entry.insert(0, self.settings["output_dir"])

        ttk.Label(win, text="Processed Directory:").pack(anchor='w', padx=10, pady=(5, 0))
        processed_entry = ttk.Entry(win, width=80)
        processed_entry.pack(fill='x', expand=True, padx=10, pady=(0, 5))
        processed_entry.insert(0, self.settings["processed_dir"])

        # Save button
        def save_and_close():
            self.settings["source_dir"] = source_entry.get()
            self.settings["output_dir"] = output_entry.get()
            self.settings["processed_dir"] = processed_entry.get()
            save_settings(self.settings)
            win.destroy()

        ttk.Button(win, text="Save", command=save_and_close).pack(pady=10)

    def process_files(self):
        selected_files = []
        for item_id in self.tree.selection():
            file_name = self.tree.item(item_id)['values'][0]
            selected_files.append(file_name)

        folder_name = self.folder_name_var.get().strip()
        if not folder_name:
            messagebox.showerror("Error", "Folder name cannot be empty.")
            return

        # Add date if selected
        if self.use_date_subfolder_var.get():
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            folder_name = os.path.join(folder_name, today)

        destination_folder = os.path.join(self.settings["output_dir"], folder_name)
        os.makedirs(destination_folder, exist_ok=True)

        if not selected_files:
            self.open_folder(destination_folder)
            return

        for file in selected_files:
            src_file = os.path.join(self.settings["source_dir"], file)
            dest_file = os.path.join(destination_folder, file)

            shutil.copy2(src_file, dest_file)
            os.makedirs(self.settings["processed_dir"], exist_ok=True)
            shutil.move(src_file, os.path.join(self.settings["processed_dir"], file))

            if self.extract_files_var.get():
                if file.endswith('.zip') or file.endswith('.tar') or file.endswith('.gz'):
                    extraction_subfolder = os.path.join(destination_folder, os.path.splitext(file)[0])
                    os.makedirs(extraction_subfolder, exist_ok=True)

                    if file.endswith('.zip'):
                        with zipfile.ZipFile(dest_file, 'r') as zip_ref:
                            zip_ref.extractall(extraction_subfolder)

                    elif file.endswith('.tar'):
                        with tarfile.open(dest_file, 'r') as tar_ref:
                            tar_ref.extractall(extraction_subfolder)

                    elif file.endswith('.gz'):
                        inner_name = os.path.splitext(file)[0]
                        inner_name = os.path.basename(inner_name)
                        gz_dest = os.path.join(extraction_subfolder, inner_name)
                        with gzip.open(dest_file, 'rb') as gz_ref:
                            with open(gz_dest, 'wb') as out_f:
                                shutil.copyfileobj(gz_ref, out_f)

                        if tarfile.is_tarfile(gz_dest):
                            with tarfile.open(gz_dest, 'r') as tar_ref:
                                tar_ref.extractall(extraction_subfolder)

        self.open_folder(destination_folder)

        # Notify
        success_popup = tk.Toplevel(self.master)
        success_popup.title("Success")
        success_popup.geometry("300x100")
        ttk.Label(success_popup, text="Files processed and extracted successfully!").pack(pady=20)
        success_popup.after(2000, lambda: [success_popup.destroy(), self.master.destroy()])

    def on_treeview_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        row_id = self.tree.identify_row(event.y)
        if not row_id:
            return

        if row_id in self.tree.selection():
            self.tree.selection_remove(row_id)
        else:
            self.tree.selection_add(row_id)
    def open_folder(self, path):
        os.startfile(path)

    def refresh_file_list(self):
        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Reload files from source directory
        self.files = [
            f for f in os.listdir(self.settings["source_dir"])
            if os.path.isfile(os.path.join(self.settings["source_dir"], f))
        ]

        for file in self.files:
            file_path = os.path.join(self.settings["source_dir"], file)
            modified_time = os.path.getmtime(file_path)
            formatted_date = datetime.datetime.fromtimestamp(modified_time).strftime('%Y-%m-%d %H:%M')

            file_type = os.path.splitext(file)[1].lstrip('.').upper() or 'NONE'

            file_size_bytes = os.path.getsize(file_path)
            if file_size_bytes >= 1024 ** 3:
                file_size = f"{file_size_bytes / (1024 ** 3):.2f} GB"
            else:
                file_size = f"{file_size_bytes / (1024 ** 2):.2f} MB"

            self.tree.insert('', 'end', values=(file, formatted_date, file_size, file_type))
if __name__ == "__main__":
    settings = load_settings()  # Load settings before ThemedTk
    root = ThemedTk(theme=settings.get("theme", "arc"))  # Use loaded theme
    # Theme is now set by ThemedTk, previous 'clam' theme is replaced.
    style = ttk.Style(root)
    # style.theme_use('clam') # No longer needed, theme is set by ThemedTk

    # --- Global Style Configurations ---
    style.configure('.', font=('Arial', 10)) # Default font for all ttk widgets

    # Specific widget type configurations
    style.configure('TLabel', font=('Arial', 10)) # Base for labels
    style.configure('TButton', font=('Arial', 10), padding=(5, 5))
    style.configure('TEntry', font=('Arial', 10), padding=(5, 5))
    style.configure('TCheckbutton', font=('Arial', 10), padding=(5, 5))

    # Treeview specific styles
    style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))
    style.configure('Treeview', font=('Arial', 10), rowheight=25) # Font for items, and row height

    # Custom style for larger buttons (like the process button)
    style.configure('Large.TButton', font=('Arial', 12, 'bold'), padding=(10, 8))

    # --- End Global Style Configurations ---

    app = FileExtractorApp(root, settings)  # Pass settings to app
    root.mainloop()
