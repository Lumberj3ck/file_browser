# File Browser

A terminal-based file browser and process manager built with [Textual](https://github.com/Textualize/textual).

## Features
- Navigate your filesystem in a tree view
- Add and remove directory bookmarks
- Fuzzy search your bookmarks
- Delete files and directories with confirmation
- View and kill running processes
- Toggle between light and dark mode

## Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/Lumberj3ck/file_browser.git
   cd file_browser
   ```
2. **Install dependencies:**
   It is recommended to use a virtual environment.
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

## Usage

Run the application with:
```sh
python main.py
```

## Keyboard Shortcuts

### Global
- `d` — Toggle dark mode
- `P` — Show process manager
- `F` — Show file tree

### File Tree
- `j` — Move cursor down
- `k` — Move cursor up
- `g` — Go to beginning of tree
- `G` — Go to end of tree
- `E` — Reveal current folder in system explorer
- `C` — Toggle node (expand/collapse)
- `-` — Go to parent directory
- `.` — Make selected folder the root
- `b` — Add bookmark for current directory
- `B` — Remove bookmark for current directory
- `f` — Show fuzzy finder for bookmarks
- `d` — Delete selected file or directory

### Process Manager
- `j` — Move cursor down
- `k` — Move cursor up
- `d` — Kill selected process

