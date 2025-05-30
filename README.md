# Organizicate (Beta v0.9.2)

![Organizicate Screenshot](https://github.com/user-attachments/assets/464cb4da-0e26-4c3e-8df8-7caf001369fd)

Organizicate is an open-source Windows desktop app for organizing files and folders by category, with a focus on flexibility and user customization. The app uses a rich set of default categories and allows you to add your own. Built with Python and Tkinter, Organizicate is designed to be packaged as a standalone `.exe` (no Python required for end users).

> **Note:**  
> This app is still in **Beta**. There may be bugs or incomplete features. Please report any issues to kerogergesazmy@gmail.com.

---

## Features

![Features Screenshot](https://github.com/user-attachments/assets/61851aad-12ca-42e1-931f-dca48550f736)

- **Organize Files and Folders**
  - Organize a single folder: Move files into subfolders by category.
  - Organize a single file: Move a file into a category folder.
  - Organize all files in a folder: Organize every file in the top-level folder (not recursive).
  - Organize all folders in a folder: Move folders into category folders based on their contents.

- **Category Management**
  - 40+ built-in default categories (cannot be deleted or have extensions changed; can be renamed).
  - Add, edit, or delete your own custom categories.
  - Assign multiple extensions to each category (supports multi-dot extensions, e.g., `.tar.gz`).
  - Search/filter categories in the manager.
  - Optional description field for user categories.

- **Export/Import Categories**
  - Export your custom categories to a JSON file.
  - Import categories from a JSON file (skips duplicates).

- **Undo Last Action**
  - Undo the last file/folder move operation (single-level undo).

- **Recent Actions Log**
  - View a log of recent actions (up to 20).

- **System Tray Minimization** *(Experimental/Beta)*
  - Minimize the app to the Windows system tray.
  - Restore or exit from the tray icon.

- **Tooltips**
  - Helpful tooltips for all buttons and fields.

- **Drag and Drop Support**
  - Drag and drop files or folders into the path entry or main window (requires `tkinterdnd2`).

- **Recent Folders Dropdown**
  - Quickly access up to 10 recently used folders.

- **Keyboard Shortcuts**
  - `Ctrl+N`: Add new category
  - `Ctrl+S`: Update category
  - `Delete`: Delete category
  - `Esc`: Clear category entry fields

---

## How to Use

1. **Download and Run**
   - Use the provided `Organizicate.exe` (no Python required).
   - If building yourself, see Packaging as an EXE.

2. **Choose an Operation**
   - Select an operation from the dropdown:
     - Organize a single folder
     - Organize a single file
     - Organize all files in a folder (top-level only)
     - Organize all folders in a folder

3. **Select Path**
   - Enter the full path, drag and drop, or use the "Browse" button.
   - Use the recent folders dropdown for quick access.

4. **Run**
   - Click "Run Operation" to organize.

5. **View Output**
   - Check the output and recent actions log for details.

6. **Undo**
   - Click "Undo Last Action" to revert the last move.

7. **Manage Categories**
   - Use the "Manage Categories" section to add, edit, or delete user categories.
   - Default categories can be renamed but not deleted or have their extensions changed.
   - Copy extensions to clipboard with the "Copy Ext" button.

8. **Export/Import Categories**
   - Export: Click "Export Categories" to save your custom categories as JSON.
   - Import: Click "Import Categories" to load categories from a JSON file.

9. **System Tray Minimization** *(Experimental/Beta)*
   - Closing the window minimizes the app to the tray (if dependencies are included).
   - Right-click the tray icon to restore or exit.

---

## Exported Categories JSON Format

When you export, only your custom categories are saved. Example:
```json
{
  "MyBooks": [".epub", ".mobi", ".pdf"],
  "Scripts": [".sh", ".bat", ".ps1"]
}
```

---

## Packaging as an EXE

You do **not** need Python installed to use the `.exe` version.

**To build your own executable:**

1. Install [PyInstaller](https://pyinstaller.org/):
    ```
    pip install pyinstaller
    ```
2. Build the executable:
    ```
    pyinstaller --noconsole --onefile --icon=organizicate.ico organizicate.py
    ```
   - The `--icon` option is optional but recommended for a better look.
   - If you do **not** provide `organizicate.ico`, the app will use a generic icon and still work.

3. Distribute the generated `dist\organizicate.exe` file.

---

## Requirements

- No Python required for end users if using the `.exe`.
- If running from source: Python 3.8+ and the following packages:
  - `ttkbootstrap` (for modern UI)
  - `pystray`, `Pillow` (for tray support, optional)
  - `tkinterdnd2` (for drag-and-drop, optional)
  - Install with:
    ```
    pip install ttkbootstrap pystray pillow tkinterdnd2
    ```

---

## Notes

- **Default categories** are not editable except for renaming.
- **Undo** only works for the last move operation.
- **System tray** feature is experimental and may not work on all systems.
- **Drag and drop** requires `tkinterdnd2` (optional).
- The app is in **Beta**: Please report bugs or unexpected behavior to the email above.
- The app **might not** organize your files the way you want. Please test it first!
- This app is **completely free** and **open-source.** Please mention my username if you use it for commercial purposes.

---

## Credits

Programmed and developed by **@theAmok**.

---

**Missing or planned features:**
- Recursive organization of subfolders (currently only top-level files/folders are organized).
- Multi-level undo.
- More advanced category rules (by file name, size, date, etc.).
- Dark mode toggle (UI support present but not enabled).
- Per-category descriptions are not saved to disk yet.

---

**Contact:** kerogergesazmy@gmail.com  
**GitHub:** https://github.com/Hotmountain/organizicate-beta

---

Let me know if you want this as a Markdown file or need further details!---

## Notes

- **Default categories** are not editable except for renaming.
- **Undo** only works for the last move operation.
- **System tray** feature is experimental and may not work on all systems.
- **Drag and drop** requires `tkinterdnd2` (optional).
- The app is in **Beta**: Please report bugs or unexpected behavior to the email above.
- The app **might not** organize your files the way you want. Please test it first!
- This app is **completely free** and **open-source.** Please mention my username if you use it for commercial purposes.

---

## Credits

Programmed and developed by **@theAmok**.

---

**Missing or planned features:**
- Recursive organization of subfolders (currently only top-level files/folders are organized).
- Multi-level undo.
- More advanced category rules (by file name, size, date, etc.).
- Dark mode toggle (UI support present but not enabled).
- Per-category descriptions are not saved to disk yet.

---

**Contact:** kerogergesazmy@gmail.com  
**GitHub:** https://github.com/Hotmountain/organizicate-beta

---

Let me know if you want this as a Markdown file or need further details!
