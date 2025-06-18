import tkinter
from tkinter import ttk

# Create a root window (can be hidden)
root = tkinter.Tk()
root.withdraw()  # Hide the main window

# Initialize ttk.Style
style = ttk.Style()

# Get the list of available themes
available_themes = style.theme_names()

# Print the list to standard output
for theme in available_themes:
    print(theme)

# It's good practice to destroy the root window, though it might not be strictly
# necessary for this script as it exits immediately after printing.
root.destroy()
