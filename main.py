import os
from pathlib import Path 
from textual.app import App, ComposeResult
from textual.widget import Widget
from textual.reactive import reactive
from textual.widgets import Header,  Footer, DirectoryTree, Tree

class Folder(Widget):
    """ Will display folder """



class StopwatchApp(App):
    CSS_PATH = "stopwatch.tcss"
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("j", "cursor_down", "Go to down the tree"),
        ("k", "cursor_up", "Go to up the tree"),
        ("-", "go_to_parrent_dir", "Go to parrent dir"),
    ]
    background_color = None
    path = reactive(Path(os.getcwd()))

    def compose(self) -> ComposeResult:
        tr: Tree = Tree("Helloo tree")
        self.tr = tr
        tr.root.expand()
        files = tr.root

        for item in self.path.iterdir():
            if item.is_file():
                files.add_leaf(item.name)
            elif item.is_dir():
                files.add(item.name, data=os.path.join(self.path, item.name))

        yield Header()
        yield tr
        yield Footer()

    def on_tree_node_expanded(self, event):
        print("on_tree_node_expanded event")
        node = event.node
        dir_entry = event.node.data
        if not dir_entry:
            return 

        d = Path(dir_entry)

        if not d.exists():
            return

        
        for item in d.iterdir():
            if item.is_file():
                node.add_leaf(item.name)
            elif item.is_dir():
                node.add(item.name, data=os.path.join(dir_entry, item.name))

    def action_go_to_parrent_dir(self):
        # self.path = self.path.parent
        print(self.tr.children)

    def action_cursor_down(self):
        self.tr.action_cursor_down()

    def action_cursor_up(self):
        self.tr.action_cursor_up()

    # def watch_path(self, new_path):

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )
    

if __name__ == "__main__":
    app = StopwatchApp()
    app.run()
