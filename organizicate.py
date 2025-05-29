import os
import shutil
import json
import threading
import queue
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from collections import defaultdict
import copy
from typing import Dict, List
# Add for tray and tooltips
import sys
try:
    import pystray  # type: ignore
    from PIL import Image  # type: ignore
except ImportError:
    pystray = None
    Image = None

CONFIG_FILE = "config.json"

# Default categories (hardcoded, cannot edit/delete)
default_file_categories = {
    "Documents": ['.doc', '.docx', '.pdf', '.txt', '.rtf', '.odt', '.pages', '.tex', '.wpd', '.wps', '.md', '.markdown', '.djvu'],
    "Spreadsheets": ['.xls', '.xlsx', '.csv', '.ods', '.numbers', '.tsv', '.dif', '.dbf'],
    "Presentations": ['.ppt', '.pptx', '.odp', '.key', '.pps', '.sldx'],
    "eBooks": ['.epub', '.mobi', '.azw3', '.fb2', '.ibooks'],
    "Images_Raster": ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.heic', '.ico', '.raw', '.cr2', '.nef', '.orf', '.sr2', '.arw', '.dng', '.pef', '.raf'],
    "Images_Vector": ['.svg', '.ai', '.eps', '.pdf', '.cdr', '.wmf', '.emf', '.fh', '.sketch'],
    "Audio": ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma', '.aiff', '.alac', '.mid', '.midi', '.ape', '.opus', '.amr', '.dsd'],
    "Video": ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.mpeg', '.mpg', '.3gp', '.vob', '.mts', '.m2ts', '.ts', '.rm', '.rmvb', '.divx', '.xvid', '.f4v'],
    "Archives": ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso', '.dmg', '.cab', '.arj', '.lz', '.lzma', '.apk', '.rpm', '.deb', '.jar', '.vhd', '.vdi'],
    "Code": ['.py', '.js', '.java', '.c', '.cpp', '.cs', '.rb', '.php', '.html', '.css', '.go', '.rs', '.swift', '.kt', '.m', '.pl', '.sh', '.bat', '.cmd', '.ts', '.tsx', '.jsx', '.lua', '.groovy', '.vbs', '.r', '.h', '.hpp', '.asm', '.s', '.d', '.erl'],
    "Fonts": ['.ttf', '.otf', '.woff', '.woff2', '.eot', '.fon', '.fnt', '.pfb', '.pfm', '.afm'],
    "System & Executables": ['.ini', '.cfg', '.conf', '.log', '.bat', '.cmd', '.sys', '.dll', '.drv', '.exe', '.msi', '.tmp', '.dat', '.bak', '.drv', '.efi'],
    "Databases": ['.db', '.sql', '.sqlite', '.sqlite3', '.mdb', '.accdb', '.dbf', '.log', '.ldf', '.ndf', '.bak'],
    "3DModels": ['.obj', '.fbx', '.stl', '.dae', '.3ds', '.blend', '.max', '.skp', '.dwg', '.dxf', '.3mf', '.ply'],
    "Scripts": ['.ps1', '.vbs', '.pl', '.r', '.lua', '.groovy', '.tcl', '.bat', '.cmd', '.sh', '.zsh', '.fish'],
    "Emails": ['.eml', '.msg', '.pst', '.ost', '.mbox'],
    "VectorDesign": ['.psd', '.xcf', '.ai', '.svg', '.indd', '.cdr', '.pdf', '.eps', '.sketch', '.afdesign'],
    "Backups": ['.bak', '.tmp', '.old', '.backup', '.swp', '.swo', '.sav', '.bkp'],
    "Web": ['.css', '.js', '.html', '.php', '.jsp', '.asp', '.aspx', '.cgi', '.pl', '.vue', '.ts', '.tsx', '.jsx', '.json', '.xml', '.yaml', '.yml'],
    "Markup": ['.md', '.markdown', '.rst', '.tex', '.txt', '.csv', '.tsv'],
    "VirtualMachines": ['.vmdk', '.vdi', '.vhd', '.vhdx', '.qcow2', '.ova', '.ovf'],
    "Minecraft": ['.mcworld', '.mcpack', '.mcaddon', '.mcmeta', '.mctemplate', '.jar', '.dat', '.nbt', '.litemod', '.mod', '.mcfunction'],
    "Certificates": ['.pem', '.crt', '.cer', '.der', '.pfx', '.p12', '.key'],
    "Logs": ['.log', '.trace', '.err', '.out'],
    "Torrent": ['.torrent'],
    "Calendar": ['.ics', '.ical'],
    "ContactCards": ['.vcf', '.vcard'],
    "GIS": ['.shp', '.shx', '.dbf', '.kml', '.kmz', '.gpx'],
    "ProjectFiles": ['.sln', '.vcxproj', '.xcodeproj', '.gradle', 'Makefile', 'CMakeLists.txt', '.idea', '.iml', '.project', '.classpath'],
    "GameFiles": ['.app', '.bat', '.com', '.jar', '.apk', '.bin', '.scr', '.gadget', '.mod', '.pak', '.sav', '.save', '.gam', '.dat', '.nes', '.snes', '.gba', '.gb', '.iso', '.xex', '.x86', '.x64', '.dll'],
    "Misc": ['.dat', '.tmp', '.cache', '.bak', '.old', '.save', '.backup', '.ini', '.cfg'],
    "Encrypted": ['.gpg', '.pgp', '.aes', '.enc', '.crypt', '.lock'],
    "Subtitles": ['.srt', '.sub', '.idx', '.ssa', '.ass'],
    "Shaders": ['.glsl', '.hlsl', '.cg', '.fx', '.shader'],
    "Docker": ['Dockerfile', '.dockerignore', '.compose', '.yml', '.yaml'],
    "Configuration": ['.json', '.yaml', '.yml', '.toml', '.ini', '.conf', '.plist', '.reg', '.desktop'],
    "Shell": ['.sh', '.bash', '.zsh', '.csh', '.ksh', '.fish'],
    "AudioProjects": ['.als', '.flp', '.logicx', '.ptx', '.aup', '.band'],
    "VideoProjects": ['.prproj', '.veg', '.aep', '.pproj', '.fcpx', '.mlt', '.drp'],
    "ImageProjects": ['.psd', '.xcf', '.kra', '.svg', '.ai', '.indd'],
    "CompressedBackups": ['.tar.gz', '.tar.bz2', '.tar.xz', '.tgz', '.tbz2', '.txz'],
    "Shortcuts": ['.lnk', '.url', '.webloc', '.desktop', '.alias', '.pif', '.scf', '.library-ms', '.folder', '.desklink'],
}

RECENT_ACTIONS_LIMIT = 20

def load_categories() -> Dict[str, List[str]]:
    """Load categories from config or default if no config found."""
    user_categories = {}
    
    if os.path.isfile(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
            # Validate loaded data (dict[str, list[str]])
            if isinstance(data, dict):
                for k, v in data.items():
                    if not isinstance(k, str) or not isinstance(v, list):
                        raise ValueError("Invalid config format")
                user_categories = data
        except Exception as e:
            print(f"Failed to load config: {e}")
            user_categories = {}
    
    # Merge default categories with user categories
    # Default categories take precedence in case of conflicts
    all_categories = copy.deepcopy(default_file_categories)
    
    # Add user categories that don't conflict with default ones
    for cat_name, extensions in user_categories.items():
        if cat_name not in default_file_categories:
            all_categories[cat_name] = extensions
    
    return all_categories

def save_categories(categories):
    """Save only user-added categories to config file."""
    try:
        # Only save categories that are not in the default set
        user_categories = {
            cat: exts for cat, exts in categories.items() 
            if cat not in default_file_categories
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(user_categories, f, indent=2)
    except Exception as e:
        print(f"Failed to save config: {e}")

def build_extension_map(categories):
    """Build reverse map from extension to category."""
    ext_map = {}
    for cat, exts in categories.items():
        for ext in exts:
            ext_map[ext.lower()] = cat
    return ext_map

class ToolTip:
    """Simple tooltip for tkinter widgets."""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert") if self.widget.winfo_ismapped() else (0,0,0,0)
        x = x + self.widget.winfo_rootx() + 25
        y = y + self.widget.winfo_rooty() + 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

class OrganizicateBeta(tk.Tk):
    def __init__(self):
        super().__init__()
        # Set icon using absolute path, handle missing icon gracefully
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "organizicate.ico")
            self.iconbitmap(icon_path)
        except Exception as e:
            print(f"Warning: Could not set window icon: {e}")
        self.title("Organizicate (Beta v0.8)")
        self.geometry("820x600")
        self.resizable(False, False)

        self.recent_actions = []
        self.action_queue = queue.Queue()
        self.operation_thread = None
        self.after(200, self.process_action_queue)

        # Load categories (default + user added)
        self.file_categories = load_categories()
        self.extension_to_category = build_extension_map(self.file_categories)

        # Track which categories are default (cannot edit/delete)
        self.default_categories = set(default_file_categories.keys())

        # Debug info
        print(f"Loaded {len(self.file_categories)} categories")
        print(f"Default categories: {len(self.default_categories)}")
        print(f"First few categories: {list(self.file_categories.keys())[:5]}")

        self.undo_stack = []  # For undo last action
        self.tray_icon = None
        self.withdrawn_for_tray = False

        self.create_widgets()
        self.refresh_category_listbox()
        # For tray support
        if pystray and Image:
            self.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

    def reload_categories(self):
        self.file_categories = load_categories()
        self.extension_to_category = build_extension_map(self.file_categories)
        self.refresh_category_listbox()
        self.status_var.set("Categories reloaded.")
        self.log("Categories reloaded from disk.")

        # Force refresh the category listbox after UI is created
        self.after(100, self.refresh_category_listbox)

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        ttk.Button(main_frame, text="Reload Categories", command=self.reload_categories).grid(row=0, column=1, sticky='e', padx=10)
        reload_btn = main_frame.winfo_children()[-1]
        ToolTip(reload_btn, "Reload categories from disk")

        # --- Operation Section ---
        ttk.Label(main_frame, text="Select organization operation:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky='w')

        self.operations = {
            "Organize a single folder": 1,
            "Organize a single file": 2,
            "Organize all files in a folder": 3,
            "Organize all folders in a folder": 4
        }
        self.operation_var = tk.StringVar()
        self.operation_dropdown = ttk.Combobox(
            main_frame, values=list(self.operations.keys()), state="readonly", width=40,
            textvariable=self.operation_var
        )
        self.operation_dropdown.grid(row=1, column=0, sticky='w')
        self.operation_dropdown.current(0)

        # Path input
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=2, column=0, pady=10, sticky='w')

        ttk.Label(path_frame, text="Enter the full path:").pack(side='left')
        self.path_entry = ttk.Entry(path_frame, width=60)
        self.path_entry.pack(side='left', padx=5)
        ttk.Button(path_frame, text="Browse", command=self.browse_path).pack(side='left')
        ToolTip(self.path_entry, "Enter the full path to a file or folder")
        browse_btn = path_frame.winfo_children()[-1]
        ToolTip(browse_btn, "Browse for a file or folder")

        # Run, Clear, Undo, Export, Import buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=0, pady=10, sticky='w')

        run_btn = ttk.Button(btn_frame, text="Run Operation", command=self.run_operation)
        run_btn.pack(side='left', padx=5)
        ToolTip(run_btn, "Run the selected organization operation")

        clear_btn = ttk.Button(btn_frame, text="Clear Output", command=self.clear_output)
        clear_btn.pack(side='left', padx=5)
        ToolTip(clear_btn, "Clear the output log")

        undo_btn = ttk.Button(btn_frame, text="Undo Last Action", command=self.undo_last_action)
        undo_btn.pack(side='left', padx=5)
        ToolTip(undo_btn, "Undo the last file/folder move operation")

        export_btn = ttk.Button(btn_frame, text="Export Categories", command=self.export_categories)
        export_btn.pack(side='left', padx=5)
        ToolTip(export_btn, "Export user categories to a file")

        import_btn = ttk.Button(btn_frame, text="Import Categories", command=self.import_categories)
        import_btn.pack(side='left', padx=5)
        ToolTip(import_btn, "Import user categories from a file")

        # --- Recent Actions Log ---
        actions_frame = ttk.LabelFrame(main_frame, text="Recent Actions Log", padding=5)
        actions_frame.grid(row=7, column=0, sticky='ew', pady=5)
        self.recent_actions_text = scrolledtext.ScrolledText(actions_frame, width=95, height=5, font=("Consolas", 9), state='disabled')
        self.recent_actions_text.pack(fill='both', expand=True)

        # --- Output Section ---
        ttk.Label(main_frame, text="Output:", font=("Arial", 12, "bold")).grid(row=4, column=0, sticky='w')
        self.output_text = scrolledtext.ScrolledText(main_frame, width=95, height=15, font=("Consolas", 10), state='disabled')
        self.output_text.grid(row=5, column=0, sticky='nsew')

        # --- Category Manager Section ---
        cat_frame = ttk.LabelFrame(main_frame, text="Manage Categories (Add/Edit/Delete User Categories)", padding=10)
        cat_frame.grid(row=6, column=0, pady=15, sticky='ew')
        cat_frame.columnconfigure(1, weight=1)

        # --- Search/Filter Entry ---
        search_frame = ttk.Frame(cat_frame)
        search_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0,5))
        ttk.Label(search_frame, text="Search:").pack(side='left')
        self.cat_search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.cat_search_var, width=20)
        search_entry.pack(side='left', padx=3)
        ToolTip(search_entry, "Type to filter categories")
        self.cat_search_var.trace_add("write", lambda *a: self.refresh_category_listbox())

        # Category listbox with frame for better layout
        listbox_frame = ttk.Frame(cat_frame)
        listbox_frame.grid(row=1, column=0, rowspan=4, sticky='nsew', padx=(0, 10))
        
        self.category_listbox = tk.Listbox(listbox_frame, height=8, width=25)
        self.category_listbox.pack(side='left', fill='both', expand=True)
        self.category_listbox.bind("<<ListboxSelect>>", self.on_category_select)
        ToolTip(self.category_listbox, "List of categories")

        # Scrollbar for listbox
        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.category_listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.category_listbox.config(yscrollcommand=scrollbar.set)

        # Entry for category name
        ttk.Label(cat_frame, text="Category Name:").grid(row=1, column=1, sticky='w')
        self.cat_name_var = tk.StringVar()
        self.cat_name_entry = ttk.Entry(cat_frame, textvariable=self.cat_name_var, width=40)
        self.cat_name_entry.grid(row=2, column=1, sticky='ew', pady=3)
        ToolTip(self.cat_name_entry, "Enter or edit the category name")

        # Entry for extensions (comma separated)
        ttk.Label(cat_frame, text="Extensions (comma separated, with dot):").grid(row=3, column=1, sticky='w')
        self.cat_ext_var = tk.StringVar()
        self.cat_ext_entry = ttk.Entry(cat_frame, textvariable=self.cat_ext_var, width=40)
        self.cat_ext_entry.grid(row=4, column=1, sticky='ew', pady=3)
        ToolTip(self.cat_ext_entry, "Enter extensions, e.g. .txt, .pdf")

        # Buttons Add / Update / Delete
        btn_cat_frame = ttk.Frame(cat_frame)
        btn_cat_frame.grid(row=5, column=1, sticky='w', pady=5)

        self.add_cat_btn = ttk.Button(btn_cat_frame, text="Add New Category", command=self.add_category)
        self.add_cat_btn.pack(side='left', padx=5)
        ToolTip(self.add_cat_btn, "Add a new user category")

        self.update_cat_btn = ttk.Button(btn_cat_frame, text="Update Category", command=self.update_category, state='disabled')
        self.update_cat_btn.pack(side='left', padx=5)
        ToolTip(self.update_cat_btn, "Update the selected category (including renaming default categories)")

        self.delete_cat_btn = ttk.Button(btn_cat_frame, text="Delete Category", command=self.delete_category, state='disabled')
        self.delete_cat_btn.pack(side='left', padx=5)
        ToolTip(self.delete_cat_btn, "Delete the selected user category")

        # --- Status Bar ---
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self, textvariable=self.status_var, relief="sunken", anchor='w')
        status_bar.pack(side='bottom', fill='x')

    def refresh_category_listbox(self):
        """Refresh the category listbox with all categories, filtered by search."""
        self.category_listbox.delete(0, 'end')
        if not self.file_categories:
            print("Warning: No categories found!")
            return
        filter_text = self.cat_search_var.get().strip().lower() if hasattr(self, 'cat_search_var') else ""
        cats_sorted = sorted(self.file_categories.keys())
        for cat in cats_sorted:
            if filter_text and filter_text not in cat.lower():
                continue
            suffix = " (default)" if cat in self.default_categories else ""
            self.category_listbox.insert('end', cat + suffix)
        print(f"Refreshed listbox with {len(cats_sorted)} categories (filtered: {filter_text})")

    def parse_extensions(self, ext_string):
        # Split by comma and clean
        exts = [e.strip().lower() if e.strip().startswith('.') else '.' + e.strip().lower() for e in ext_string.split(',') if e.strip()]
        # Allow extensions with multiple dots (e.g., .tar.gz)
        valid_exts = []
        for e in exts:
            if len(e) >= 2 and e[0] == '.' and all(c.isalnum() or c == '.' for c in e[1:]):
                valid_exts.append(e)
        return valid_exts

    def on_category_select(self, event):
        sel = self.category_listbox.curselection()
        if not sel:
            self.cat_name_var.set("")
            self.cat_ext_var.set("")
            self.update_cat_btn.config(state='disabled')
            self.delete_cat_btn.config(state='disabled')
            self.add_cat_btn.config(state='normal')
            return
        
        idx = sel[0]
        cat_name_with_suffix = self.category_listbox.get(idx)
        cat_name = cat_name_with_suffix.replace(" (default)", "")
        self.cat_name_var.set(cat_name)
        exts = self.file_categories.get(cat_name, [])
        self.cat_ext_var.set(", ".join(exts))

        # Enable/disable buttons based on default or user category
        if cat_name in self.default_categories:
            self.update_cat_btn.config(state='normal')  # Allow renaming default
            self.delete_cat_btn.config(state='disabled')
            self.add_cat_btn.config(state='normal')
            self.cat_ext_entry.config(state='disabled')  # Can't edit extensions for default
            ToolTip(self.update_cat_btn, "Rename default categories (extensions not editable)")
        else:
            self.update_cat_btn.config(state='normal')
            self.delete_cat_btn.config(state='normal')
            self.add_cat_btn.config(state='disabled')
            self.cat_ext_entry.config(state='normal')

    def add_category(self):
        name = self.cat_name_var.get().strip()
        exts = self.cat_ext_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Category name cannot be empty.")
            return
        if name in self.file_categories:
            messagebox.showerror("Error", f"Category '{name}' already exists.")
            return
        ext_list = self.parse_extensions(exts)
        if not ext_list:
            messagebox.showerror("Error", "Please enter at least one valid extension (e.g. .txt).")
            return
        
        self.file_categories[name] = ext_list
        save_categories(self.file_categories)
        self.extension_to_category = build_extension_map(self.file_categories)
        self.refresh_category_listbox()
        self.clear_category_entries()
        self.log(f"Added new category '{name}' with extensions: {', '.join(ext_list)}")
        self.status_var.set(f"Added new category '{name}'")

    def update_category(self):
        sel = self.category_listbox.curselection()
        if not sel:
            messagebox.showwarning("Warning", "No category selected to update.")
            return
        
        idx = sel[0]
        old_name_with_suffix = self.category_listbox.get(idx)
        old_name = old_name_with_suffix.replace(" (default)", "")
        
        new_name = self.cat_name_var.get().strip()
        exts = self.cat_ext_var.get().strip()
        
        if not new_name:
            messagebox.showerror("Error", "Category name cannot be empty.")
            return
        
        # If new_name is different and exists, error
        if new_name != old_name and new_name in self.file_categories:
            messagebox.showerror("Error", f"Category '{new_name}' already exists.")
            return

        # For default categories, allow renaming but not editing extensions
        if old_name in self.default_categories:
            if new_name == old_name:
                messagebox.showinfo("Info", "No changes to update.")
                return
            # Rename default category
            self.file_categories[new_name] = self.file_categories.pop(old_name)
            self.default_categories.remove(old_name)
            self.default_categories.add(new_name)
            self.log(f"Renamed default category '{old_name}' to '{new_name}'")
            self.status_var.set(f"Renamed default category '{new_name}'")
        else:
            ext_list = self.parse_extensions(exts)
            if not ext_list:
                messagebox.showerror("Error", "Please enter at least one valid extension (e.g. .txt).")
                return
            if new_name != old_name:
                self.file_categories.pop(old_name)
            self.file_categories[new_name] = ext_list
            self.log(f"Updated category '{old_name}' to '{new_name}' with extensions: {', '.join(ext_list)}")
            self.status_var.set(f"Updated category '{new_name}'")
        save_categories(self.file_categories)
        self.extension_to_category = build_extension_map(self.file_categories)
        self.refresh_category_listbox()
        self.clear_category_entries()

    def delete_category(self):
        sel = self.category_listbox.curselection()
        if not sel:
            messagebox.showwarning("Warning", "No category selected to delete.")
            return
        
        idx = sel[0]
        name_with_suffix = self.category_listbox.get(idx)
        name = name_with_suffix.replace(" (default)", "")
        
        if name in self.default_categories:
            messagebox.showerror("Error", "Cannot delete default categories.")
            return
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete category '{name}'?"):
            self.file_categories.pop(name, None)
            save_categories(self.file_categories)
            self.extension_to_category = build_extension_map(self.file_categories)
            self.refresh_category_listbox()
            self.clear_category_entries()
            self.log(f"Deleted category '{name}'")
            self.status_var.set(f"Deleted category '{name}'")

    def clear_category_entries(self):
        self.cat_name_var.set("")
        self.cat_ext_var.set("")
        self.add_cat_btn.config(state='normal')
        self.update_cat_btn.config(state='disabled')
        self.delete_cat_btn.config(state='disabled')
        self.category_listbox.selection_clear(0, 'end')

    def add_recent_action(self, message):
        self.recent_actions.append(message)
        if len(self.recent_actions) > RECENT_ACTIONS_LIMIT:
            self.recent_actions = self.recent_actions[-RECENT_ACTIONS_LIMIT:]
        self.update_recent_actions_log()

    def update_recent_actions_log(self):
        self.recent_actions_text.config(state='normal')
        self.recent_actions_text.delete('1.0', 'end')
        for msg in self.recent_actions[-RECENT_ACTIONS_LIMIT:]:
            self.recent_actions_text.insert('end', msg + "\n")
        self.recent_actions_text.see('end')
        self.recent_actions_text.config(state='disabled')
    
    def browse_path(self):
        op = self.operations[self.operation_var.get()]
        if op in (1, 3, 4):  # Folder related operations
            folder = filedialog.askdirectory()
            if folder:
                self.path_entry.delete(0, 'end')
                self.path_entry.insert(0, folder)
        elif op == 2:  # Single file
            file = filedialog.askopenfilename()
            if file:
                self.path_entry.delete(0, 'end')
                self.path_entry.insert(0, file)

    def clear_output(self):
        self.output_text.config(state='normal')
        self.output_text.delete('1.0', 'end')
        self.output_text.config(state='disabled')
        self.status_var.set("Output cleared.")

    def log(self, message):
        self.output_text.config(state='normal')
        self.output_text.insert('end', message + "\n")
        self.output_text.see('end')
        self.output_text.config(state='disabled')

    def log_summary(self, count_moved):
        """Log a summary of moved files/folders by category."""
        if not count_moved:
            self.log("No files or folders were moved.")
            return
        summary_lines = ["Summary of moved items:"]
        for cat, count in sorted(count_moved.items()):
            summary_lines.append(f"  {cat}: {count}")
        self.log("\n".join(summary_lines))

    def run_operation(self):
        path = self.path_entry.get().strip()
        if not path:
            messagebox.showerror("Error", "Please enter a valid path.")
            return
        op = self.operations[self.operation_var.get()]
        self.status_var.set("Running operation...")
        self.log(f"Operation: {self.operation_var.get()}")
        self.log(f"Target Path: {path}")

        # Run in background thread to avoid freezing UI
        if self.operation_thread and self.operation_thread.is_alive():
            messagebox.showwarning("Warning", "An operation is already running.")
            return
        self.operation_thread = threading.Thread(
            target=self._run_operation_thread,
            args=(op, path),
            daemon=True
        )
        self.operation_thread.start()

    def _run_operation_thread(self, op, path):
        try:
            if op == 1:
                self.organize_single_folder(path)
            elif op == 2:
                self.organize_single_file(path)
            elif op == 3:
                self.organize_all_files_in_folder(path)
            elif op == 4:
                self.organize_all_folders_in_folder(path)
            else:
                self.action_queue.put(("status", "Unknown operation selected."))
                self.action_queue.put(("log", "Unknown operation selected."))
                return
            self.action_queue.put(("status", "Operation completed."))
        except Exception as e:
            self.action_queue.put(("status", "Error occurred."))
            self.action_queue.put(("log", f"Error: {e}"))

    def process_action_queue(self):
        try:
            while True:
                action, msg = self.action_queue.get_nowait()
                if action == "log":
                    self.log(msg)
                elif action == "status":
                    self.status_var.set(msg)
        except queue.Empty:
            pass
        self.after(100, self.process_action_queue)

    # === Organization methods ===

    def get_category_for_file(self, filename):
        ext = os.path.splitext(filename)[1].lower()
        return self.extension_to_category.get(ext, "Other")

    def ensure_folder(self, base_path, folder_name):
        folder_path = os.path.join(base_path, folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        return folder_path

    def organize_single_folder(self, folder_path):
        if not os.path.isdir(folder_path):
            raise ValueError(f"'{folder_path}' is not a valid folder path.")
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        if not files:
            self.log("No files found in the folder.")
            return
        count_moved = defaultdict(int)
        undo_ops = []
        for file in files:
            category = self.get_category_for_file(file)
            dest_folder = self.ensure_folder(folder_path, category)
            src = os.path.join(folder_path, file)
            dst = os.path.join(dest_folder, file)
            try:
                shutil.move(src, dst)
                self.log(f"Moved file '{file}' to folder '{category}'.")
                count_moved[category] += 1
                undo_ops.append((src, dst))
            except Exception as e:
                self.log(f"Failed to move '{file}': {e}")
        if undo_ops:
            self.undo_stack.append(undo_ops)
        self.log_summary(count_moved)

    def organize_single_file(self, file_path):
        if not os.path.isfile(file_path):
            raise ValueError(f"'{file_path}' is not a valid file.")
        folder_path = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        category = self.get_category_for_file(file_name)
        dest_folder = self.ensure_folder(folder_path, category)
        dst = os.path.join(dest_folder, file_name)
        undo_ops = []
        try:
            shutil.move(file_path, dst)
            self.log(f"Moved file '{file_name}' to folder '{category}'.")
            self.log_summary({category: 1})
            undo_ops.append((file_path, dst))
        except Exception as e:
            self.log(f"Failed to move '{file_name}': {e}")
        if undo_ops:
            self.undo_stack.append(undo_ops)

    def organize_all_files_in_folder(self, folder_path):
        if not os.path.isdir(folder_path):
            raise ValueError(f"'{folder_path}' is not a valid folder path.")
        count_moved = defaultdict(int)
        undo_ops = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                src = os.path.join(root, file)
                category = self.get_category_for_file(file)
                dest_folder = self.ensure_folder(root, category)  # Use root, not folder_path
                dst = os.path.join(dest_folder, file)
                if os.path.abspath(src) == os.path.abspath(dst):
                    continue  # skip if same file
                try:
                    shutil.move(src, dst)
                    self.action_queue.put(("log", f"Moved file '{file}' to folder '{category}'."))
                    count_moved[category] += 1
                    undo_ops.append((src, dst))
                except Exception as e:
                    self.action_queue.put(("log", f"Failed to move '{file}': {e}"))
        if undo_ops:
            self.undo_stack.append(undo_ops)
        self.action_queue.put(("log", self._format_log_summary(count_moved)))

    def organize_all_folders_in_folder(self, folder_path):
        if not os.path.isdir(folder_path):
            raise ValueError(f"'{folder_path}' is not a valid folder path.")
        count_moved = 0
        undo_ops = []
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isdir(item_path):
                category = self.get_category_for_folder(item_path)
                dest_folder = self.ensure_folder(folder_path, category)
                dst = os.path.join(dest_folder, item)
                if os.path.abspath(item_path) == os.path.abspath(dst):
                    continue
                try:
                    common = os.path.commonpath([os.path.abspath(item_path), os.path.abspath(dst)])
                    if common == os.path.abspath(item_path):
                        continue
                except ValueError:
                    pass
                try:
                    shutil.move(item_path, dst)
                    self.action_queue.put(("log", f"Moved folder '{item}' to folder '{category}'."))
                    count_moved += 1
                    undo_ops.append((item_path, dst))
                except Exception as e:
                    self.action_queue.put(("log", f"Failed to move folder '{item}': {e}"))
        if undo_ops:
            self.undo_stack.append(undo_ops)
        self.action_queue.put(("log", f"Moved {count_moved} folders."))

    # --- Export/Import Categories ---
    def export_categories(self):
        user_categories = {cat: exts for cat, exts in self.file_categories.items() if cat not in default_file_categories}
        if not user_categories:
            messagebox.showinfo("Export Categories", "No user categories to export.")
            return
        file = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")], title="Export Categories")
        if file:
            try:
                with open(file, "w") as f:
                    json.dump(user_categories, f, indent=2)
                self.status_var.set("Categories exported.")
                self.log(f"Exported user categories to {file}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export: {e}")

    def import_categories(self):
        file = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")], title="Import Categories")
        if file:
            try:
                with open(file, "r") as f:
                    data = json.load(f)
                if not isinstance(data, dict):
                    raise ValueError("Invalid format")
                # Merge, skip conflicts
                added = 0
                for cat, exts in data.items():
                    if cat not in self.file_categories:
                        self.file_categories[cat] = exts
                        added += 1
                save_categories(self.file_categories)
                self.extension_to_category = build_extension_map(self.file_categories)
                self.refresh_category_listbox()
                self.status_var.set(f"Imported {added} categories.")
                self.log(f"Imported {added} categories from {file}")
            except Exception as e:
                messagebox.showerror("Import Error", f"Failed to import: {e}")

    # --- Undo Last Action ---
    def undo_last_action(self):
        if not self.undo_stack:
            messagebox.showinfo("Undo", "No action to undo.")
            return
        last = self.undo_stack.pop()
        try:
            # last: list of (src, dst) tuples (undo: move dst -> src)
            for src, dst in reversed(last):
                if os.path.exists(dst):
                    shutil.move(dst, src)
                    self.log(f"Undo: moved '{os.path.basename(dst)}' back to '{os.path.dirname(src)}'")
            self.status_var.set("Undo completed.")
        except Exception as e:
            self.log(f"Undo failed: {e}")
            self.status_var.set("Undo failed.")

    # --- System Tray Minimization ---
    def minimize_to_tray(self):
        if not pystray or not Image:
            self.destroy()
            return
        self.withdraw()
        self.withdrawn_for_tray = True
        image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "organizicate.ico")
        try:
            icon_img = Image.open(image_path)
        except Exception:
            icon_img = Image.new("RGB", (32,32), color="gray")
        menu = pystray.Menu(
            pystray.MenuItem("Restore", self.restore_from_tray),
            pystray.MenuItem("Exit", self.exit_from_tray)
        )
        self.tray_icon = pystray.Icon("organizicate", icon_img, "Organizicate", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def restore_from_tray(self, icon=None, item=None):
        self.after(0, self._restore_window)

    def _restore_window(self):
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None
        self.deiconify()
        self.withdrawn_for_tray = False

    def exit_from_tray(self, icon=None, item=None):
        self.after(0, self.destroy)

    def destroy(self):
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None
        super().destroy()

# Lines 350-368 (example)
def categorize_file(filename, extension_to_category):
    ext = os.path.splitext(filename)[1].lower()
    return extension_to_category.get(ext, "Other")

def categorize_folder(folder_path, extension_to_category):
    if not os.path.isdir(folder_path):
        return "Other"
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    if not files:
        return "Empty"
    cat_count = defaultdict(int)
    for file in files:
        cat = categorize_file(file, extension_to_category)
        cat_count[cat] += 1
    if not cat_count:
        return "Other"
    if len(cat_count) == 1:
        return next(iter(cat_count))
    most_common = max(cat_count.items(), key=lambda x: x[1])
    if most_common[1] > len(files) // 2:
        return most_common[0]
    return "Mixed"

# Main execution
if __name__ == "__main__":
    try:
        app = OrganizicateBeta()
        app.mainloop()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("Program ended.")
