import os
from pathlib import Path
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import Header, Footer, Tree


class StopwatchApp(App):
    CSS_PATH = "stopwatch.tcss"
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("j", "cursor_down", "Go to down the tree"),
        ("k", "cursor_up", "Go to up the tree"),
        ("g", "cursor_to_the_begining", "Move cursor to the begining of tree"),
        ("G", "cursor_to_the_end", "Move cursor to the end of tree"),
        ("C", "toggle_node", "Toggle node"),
        ("-", "go_to_parrent_dir", "Go to parrent dir"),
    ]
    background_color = None
    path = reactive(Path(os.getcwd()))


    def compose(self) -> ComposeResult:
        tr: Tree = Tree("Helloo tree")
        self.tr = tr

        yield Header()
        yield tr
        yield Footer()
    
    def render_tree(self, dir_path, node):
        if node is not self.tr.root and node.children:
            node.remove_children()
        for item in dir_path.iterdir():
            if item.is_file():
                node.add_leaf(item.name)
            elif item.is_dir():
                node.add(item.name, data=os.path.join(dir_path, item.name))
        if node is self.tr.root:
            self.tr.root.expand()

    def on_tree_node_expanded(self, event):
        print("on_tree_node_expanded event")
        node = event.node
        dir_entry = event.node.data

        if not dir_entry:
            print("Skippedn")
            return

        d = Path(dir_entry)

        if not d.exists():
            return

        self.render_tree(d, node)


    def action_go_to_parrent_dir(self):
        self.path = self.path.parent

    def watch_path(self):
        print("On root wathc")
        self.tr.root.remove_children()
        self.render_tree(self.path, self.tr.root)


    def action_cursor_down(self):
        self.tr.action_cursor_down()

    def action_cursor_up(self):
        self.tr.action_cursor_up()

    def action_cursor_to_the_begining(self):
        self.tr.move_cursor(self.tr.root)

    def action_cursor_to_the_end(self):
        self.tr.move_cursor(self.tr.root.children[-1])

    def action_toggle_node(self):
        self.tr.action_toggle_node()

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )


if __name__ == "__main__":
    app = StopwatchApp()
    app.run()
