# Organizicate (Beta v0.7)

Organizicate is an open-source Windows desktop app for organizing files and folders by category, with a focus on flexibility and user customization. It uses a rich set of default categories and allows you to add your own. The app is built with Python and Tkinter, and is designed to be packaged as a standalone `.exe` (no Python required for end users).

> [!NOTE]
> This app is still in **Beta.** Which means that there will be a few bugs or incomplete features, please report any bugs or unexpected behaviour on my email (kerogergesazmy@gmail.com)

---

## Features

- **Organize Files and Folders**
  - Organize a single folder: Move files into subfolders by category.
  - Organize a single file: Move a file into a category folder.
  - Organize all files in a folder (recursive): Organize every file in all subfolders.
  - Organize all folders in a folder: Move folders into category folders based on their contents.

- **Category Management**
  - 40+ built-in default categories (cannot be deleted or edited except for renaming).
  - Add, edit, or delete your own custom categories.
  - Assign multiple extensions to each category.
  - Search/filter categories in the manager.

- **Export/Import Categories**
  - Export your custom categories to a JSON file.
  - Import categories from a JSON file (skips duplicates).

- **Undo Last Action**
  - Undo the last file/folder move operation.

- **Recent Actions Log**
  - View a log of recent actions (up to 20).

- **System Tray Minimization** *(Experimental/Beta)*
  - Minimize the app to the Windows system tray.
  - Restore or exit from the tray icon.

- **Tooltips**
  - Helpful tooltips for all buttons and fields.

---

## How to Use

1. **Download and Run**
   - Use the provided `Organizicate.exe` (no Python required).
   - If building yourself, use PyInstaller (see below).

2. **Choose an Operation**
   - Select an operation from the dropdown:
     - Organize a single folder
     - Organize a single file
     - Organize all files in a folder (recursive)
     - Organize all folders in a folder

3. **Select Path**
   - Enter the full path or use the "Browse" button.

4. **Run**
   - Click "Run Operation" to organize.

5. **View Output**
   - Check the output and recent actions log for details.

6. **Undo**
   - Click "Undo Last Action" to revert the last move.

7. **Manage Categories**
   - Use the "Manage Categories" section to add, edit, or delete user categories.
   - Default categories can be renamed but not deleted or have their extensions changed.

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

## Is the ICO file required?

- **No, the `.ico` file is not required.**
- If `organizicate.ico` is missing, the app will use a generic icon and still function normally.
- For best appearance, place `organizicate.ico` in the same folder as the `.exe`.

---

## Requirements

- No Python required for end users if using the `.exe`.
- If running from source: Python 3.8+ and the following packages:
  - `pystray`, `Pillow` (for tray support, optional)
  - Install with:
    ```
    pip install pystray pillow
    ```

---

## Notes

- **Default categories** are not editable except for renaming.
- **Undo** only works for the last move operation.
- **System tray** feature is experimental and may not work on all systems.
- Again, the app is in **Beta**: Please report bugs or unexpected behavior on my email above.
- The app **might not** organize your files the way you want. So please test it first before you try it!
- This app is **completely free** and **open-source.** Please mention my username if you are going to use it for commercial-use.

---

## Credits

Programmed and developed by @theAmok.
