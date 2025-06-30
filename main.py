import os
import subprocess
from pathlib import Path
from textual.app import App, ComposeResult
from textual.reactive import reactive
from typing import  ClassVar, List, Optional
from textual.widgets import Header, Footer, Tree, DirectoryTree, Input, Static
from textual.binding import Binding, BindingType
from textual.containers import Container
from textual.widget import Widget
from textual import work
from textual.message import Message
from process_manager import ProcessManager

class BookmarkManager:
    def __init__(self):
        self.bookmarks: List[Path] = []
    
    def add_bookmark(self, path: Path) -> None:
        if path not in self.bookmarks:
            self.bookmarks.append(path)
    
    def remove_bookmark(self, path: Path) -> None:
        if path in self.bookmarks:
            self.bookmarks.remove(path)
    
    def get_bookmarks(self) -> List[Path]:
        return self.bookmarks.copy()
    
    def is_bookmarked(self, path: Path) -> bool:
        return path in self.bookmarks

class FuzzyFinder(Widget):
    def __init__(self, bookmarks: List[Path]):
        super().__init__()
        self.bookmarks = bookmarks
        self.filtered_bookmarks: List[Path] = []
        self.selected_index = 0
        self.is_visible = False
    
    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search bookmarks...", id="fuzzy_input")
        yield Container(id="results_container")
    
    def on_input_changed(self, event: Input.Changed) -> None:
        query = event.value.lower()
        if query:
            self.filtered_bookmarks = [
                bookmark for bookmark in self.bookmarks
                if query in str(bookmark).lower() or query in bookmark.name.lower()
            ]
        else:
            self.filtered_bookmarks = self.bookmarks.copy()
        
        if self.filtered_bookmarks:
            self.selected_index = min(self.selected_index, len(self.filtered_bookmarks) - 1)
        else:
            self.selected_index = 0
        
        self.update_results_display()
    
    def update_results_display(self) -> None:
        results_container = self.query_one("#results_container")
        results_container.remove_children()
        
        for i, bookmark in enumerate(self.filtered_bookmarks):
            is_selected = i == self.selected_index
            style = "bold reverse" if is_selected else ""
            result_widget = Static()
            result_widget.styles.content_align = ("left", "middle")
            result_widget.styles.padding = (0, 1)
            result_widget.styles.background = "blue" if is_selected else "transparent"
            result_widget.styles.color = "white" 
            result_widget.styles.bold = is_selected
            
            # Display bookmark name and path
            display_text = f"📁 {bookmark.name}\n  {bookmark}"
            result_widget.update(display_text)
            results_container.mount(result_widget)
    
    def on_key(self, event) -> None:
        if not self.is_visible:
            return
        
        if event.key == "escape":
            self.hide_finder()
        elif event.key == "enter" and self.filtered_bookmarks:
            selected_bookmark = self.filtered_bookmarks[self.selected_index]
            self.hide_finder()
            self.post_message(self.BookmarkSelected(selected_bookmark))
        elif event.key == "up":
            if self.filtered_bookmarks:
                self.selected_index = (self.selected_index - 1) % len(self.filtered_bookmarks)
                self.update_results_display()
        elif event.key == "down":
            if self.filtered_bookmarks:
                self.selected_index = (self.selected_index + 1) % len(self.filtered_bookmarks)
                self.update_results_display()
    
    def show_finder(self) -> None:
        self.is_visible = True
        self.filtered_bookmarks = self.bookmarks.copy()
        self.selected_index = 0
        self.styles.display = "block"
        self.update_results_display()
        self.query_one("#fuzzy_input").focus()
    
    def hide_finder(self) -> None:
        self.is_visible = False
        self.styles.display = "none"
        self.query_one("#fuzzy_input").value = ""
        self.query_one("#results_container").remove_children()
    
    class BookmarkSelected(Message):
        def __init__(self, bookmark_path: Path):
            super().__init__()
            self.bookmark_path = bookmark_path

class FileTree(Tree):
    ICON_NODE_EXPANDED = "📂 "
    ICON_NODE = "📁 "
    ICON_FILE = "📄 "
    ICON_BOOKMARK = "🔖 "

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("j", "cursor_down", "Go to down the tree"),
        Binding("k", "cursor_up", "Go to up the tree"),
        Binding("g", "cursor_to_the_begining", "Move cursor to the begining of tree", show=False),
        Binding("G", "cursor_to_the_end", "Move cursor to the end of tree", show=False),
        Binding("E", "reveal_in_explorer", "Reveal current folder in explorer", show=False),
        Binding("C", "toggle_node", "Toggle node", show=False),
        Binding("-", "go_to_parrent_dir", "Go to parrent dir", show=False),
        Binding(".", "make_root_under_cursor", "Make selected folder root", show=False),
        Binding("b", "add_bookmark", "Add bookmark for current directory", show=False),
        Binding("B", "remove_bookmark", "Remove bookmark for current directory", show=False),
        Binding("f", "show_fuzzy_finder", "Show fuzzy finder for bookmarks", show=False),
        Binding("d", "delete_selected", "Delete selected file or directory", show=False),
    ]
    path: reactive = reactive(Path(os.getcwd()))

    def __init__(self, bookmark_manager: BookmarkManager):
        super().__init__(str(""))
        self.bookmark_manager = bookmark_manager

    def render_tree(self, dir_path, node):
        if node is not self.root and node.children:
            node.remove_children()
        for item in dir_path.iterdir():
            if item.is_file():
                node.add_leaf(item.name, data=os.path.join(dir_path, item.name))
            elif item.is_dir():
                bookmark_icon = self.ICON_BOOKMARK if self.bookmark_manager.is_bookmarked(item) else ""
                node.add(f"{bookmark_icon}{item.name}", data=os.path.join(dir_path, item.name))
        if node is self.root:
            self.root.expand()
        self.focus()

    def on_tree_node_expanded(self, event):
        node = event.node
        dir_entry = event.node.data

        if not dir_entry:
            return

        d = Path(dir_entry)

        if not d.exists():
            return

        self.render_tree(d, node)

    def action_make_root_under_cursor(self):
        if not self.cursor_node:
            return 

        data = self.cursor_node.data 

        if not data:
            return 
        
        selected_dir = Path(data)

        if not selected_dir.is_dir():
            return

        self.path = selected_dir

    def action_go_to_parrent_dir(self):
        self.path = self.path.parent

    def action_add_bookmark(self):
        if not self.cursor_node:
            return
        
        data = self.cursor_node.data
        
        if not data:
            return
        
        selected_path = Path(data)
        
        if selected_path.is_dir():
            self.bookmark_manager.add_bookmark(selected_path)
            self.refresh_tree()

    def action_remove_bookmark(self):
        if not self.cursor_node:
            return
        
        data = self.cursor_node.data
        
        if not data:
            return
        
        selected_path = Path(data)
        
        if selected_path.is_dir():
            self.bookmark_manager.remove_bookmark(selected_path)
            self.refresh_tree()

    def action_show_fuzzy_finder(self):
        self.post_message(self.ShowFuzzyFinder())

    def refresh_tree(self):
        self.watch_path()

    def watch_path(self):
        self.root.remove_children()
        self.render_tree(self.path, self.root)

    def action_cursor_to_the_begining(self):
        if self.root.children:
            self.move_cursor(self.root.children[0])

    def action_cursor_to_the_end(self):
        if self.root.children:
            self.move_cursor(self.root.children[-1])

    def action_reveal_in_explorer(self):
        subprocess.run(["explorer", str(self.path)])

    def action_delete_selected(self):
        if not self.cursor_node:
            return
        data = self.cursor_node.data

        print(self.cursor_node)
        if not data:
            return
        selected_path = Path(data)

        self.post_message(self.ConfirmDelete(selected_path))

    class ShowFuzzyFinder(Message):
        pass

    class ConfirmDelete(Message):
        def __init__(self, path: Path):
            super().__init__()
            self.path = path

class ConfirmDialog(Widget):
    class Confirmed(Message):
        def __init__(self, path: Path):
            super().__init__()
            self.path = path
    class Cancelled(Message):
        pass

    def __init__(self, path: Path):
        super().__init__()
        self.path = path
        self.styles.display = "block"
        self.styles.position = "absolute"
        self.styles.top = "40%"
        self.styles.left = "30%"
        self.styles.width = "40%"
        self.styles.background = "#222"
        self.styles.color = "white"
        self.styles.border =  ("heavy", "white") 
        self.styles.padding = (1, 2)

    def compose(self) -> ComposeResult:
        yield Static(f"Are you sure you want to delete '{self.path.name}'?", id="confirm_text")
        yield Container(
            Input(placeholder="Type 'y' for Yes or 'n' for No", id="confirm_input"),
            id="confirm_input_container"
        )

    def on_mount(self) -> None:
        # Focus the input after the widget is mounted
        input_widget = self.query_one("#confirm_input", Input)
        input_widget.focus()

    def on_input_submitted(self, event: Input.Submitted):
        value = event.value.strip().lower()
        if value == "y":
            self.post_message(self.Confirmed(self.path))
            self.remove()
        elif value == "n":
            self.post_message(self.Cancelled())
            self.remove()
        else:
            # Optionally clear input or show error
            event.input.value = ""

class FileBrowser(App):
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("d", "toggle_dark", "Toggle dark mode"),
        Binding("P", "show_process_manager", "Opens process manager"),
        Binding("F", "show_file_tree", "Show file tree"),
    ]
    background_color = None

    def __init__(self):
        super().__init__()
        self.bookmark_manager = BookmarkManager()
        self.fuzzy_finder: Optional[FuzzyFinder] = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield FileTree(self.bookmark_manager)
        yield ProcessManager()
        yield Footer()

    def on_mount(self) -> None:
        self.fuzzy_finder = FuzzyFinder(self.bookmark_manager.get_bookmarks())
        self.fuzzy_finder.styles.display = "none"
        self.fuzzy_finder.styles.position = "absolute"
        self.fuzzy_finder.styles.top = "10%"
        self.fuzzy_finder.styles.left = "20%"
        self.fuzzy_finder.styles.width = "60%"
        self.fuzzy_finder.styles.height = "auto"
        # self.fuzzy_finder.styles.background = "141414"
        # self.fuzzy_finder.styles.border = "646464"
        # self.fuzzy_finder.styles.border_title = "Bookmarks"
        # self.fuzzy_finder.styles.z_index = "1000"
        # self.fuzzy_finder.styles.padding = "1 1"
        self.query_one(ProcessManager).display = False
        self.mount(self.fuzzy_finder)

    def on_file_tree_show_fuzzy_finder(self, event: FileTree.ShowFuzzyFinder) -> None:
        if self.fuzzy_finder:
            self.fuzzy_finder.bookmarks = self.bookmark_manager.get_bookmarks()
            self.fuzzy_finder.show_finder()

    def on_process_manager_show_file_tree(self):
        self.query_one(FileTree).display = True
        self.query_one(ProcessManager).display = False

    def on_fuzzy_finder_bookmark_selected(self, event: FuzzyFinder.BookmarkSelected) -> None:
        file_tree = self.query_one(FileTree)
        file_tree.path = event.bookmark_path

    def action_show_file_tree(self):
        self.query_one(FileTree).display = True
        self.query_one(FileTree).focus()
        self.query_one(ProcessManager).display = False
        self.query_one(ProcessManager).stop_update()

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_show_process_manager(self):
        self.query_one(FileTree).display = False
        self.query_one(ProcessManager).display = True
        self.query_one(ProcessManager).on_focus()
        self.query_one(ProcessManager).resume_update()

    def on_file_tree_confirm_delete(self, event: FileTree.ConfirmDelete) -> None:
        # Show confirmation dialog
        dialog = ConfirmDialog(event.path)
        self.mount(dialog)
        # dialog.on_focus()
        self.confirm_dialog = dialog
        self.confirm_delete_path = event.path

    def on_confirm_dialog_confirmed(self, event: ConfirmDialog.Confirmed) -> None:
        path = event.path
        try:
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                import shutil
                shutil.rmtree(path)
        except Exception as e:
            pass  # Optionally show error
        self.query_one(FileTree).refresh_tree()
        self.confirm_dialog = None
        self.confirm_delete_path = None

    def on_confirm_dialog_cancelled(self, event: ConfirmDialog.Cancelled) -> None:
        if hasattr(self, 'confirm_dialog') and self.confirm_dialog:
            self.confirm_dialog.remove()
            self.confirm_dialog = None
            self.confirm_delete_path = None

if __name__ == "__main__":
    app = FileBrowser()
    app.run()
