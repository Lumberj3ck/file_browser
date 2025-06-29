import os
import subprocess
from pathlib import Path
from textual.app import App, ComposeResult
from textual.reactive import reactive
from typing import  ClassVar
from textual.widgets import Header, Footer, Tree, DirectoryTree
from textual.binding import Binding, BindingType

class FileTree(Tree):
    ICON_NODE_EXPANDED = "📂 "
    ICON_NODE = "📁 "
    ICON_FILE = "📄 "

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("j", "cursor_down", "Go to down the tree"),
        Binding("k", "cursor_up", "Go to up the tree"),
        Binding("g", "cursor_to_the_begining", "Move cursor to the begining of tree", show=False),
        Binding("G", "cursor_to_the_end", "Move cursor to the end of tree", show=False),
        Binding("E", "reveal_in_explorer", "Reveal current folder in explorer", show=False),
        Binding("C", "toggle_node", "Toggle node", show=False),
        Binding("-", "go_to_parrent_dir", "Go to parrent dir", show=False),
        Binding(".", "make_root_under_cursor", "Make selected folder root", show=False),
    ]
    path: reactive = reactive(Path(os.getcwd()))

    def __init__(self):
        super().__init__(str(""))

    def render_tree(self, dir_path, node):
        if node is not self.root and node.children:
            node.remove_children()
        for item in dir_path.iterdir():
            if item.is_file():
                node.add_leaf(item.name)
            elif item.is_dir():
                node.add(item.name, data=os.path.join(dir_path, item.name))
        if node is self.root:
            self.root.expand()

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

    def watch_path(self):
        self.root.remove_children()
        self.render_tree(self.path, self.root)

    def action_cursor_to_the_begining(self):
        self.move_cursor(self.root.children[0])

    def action_cursor_to_the_end(self):
        self.move_cursor(self.root.children[-1])
    def action_reveal_in_explorer(self):
        subprocess.run(["explorer", str(self.path)])


class FileBrowser(App):
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("d", "toggle_dark", "Toggle dark mode"),
    ]
    background_color = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield FileTree()
        yield Footer()
    


    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )


if __name__ == "__main__":
    app = FileBrowser()
    app.run()
