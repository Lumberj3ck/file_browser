import os
from pathlib import Path 
from textual.app import App, ComposeResult
from textual.widget import Widget
from textual.reactive import reactive
from textual.widgets import Header,  Footer, DirectoryTree

class Folder(Widget):
    """ Will display folder """



class StopwatchApp(App):
    CSS_PATH = "stopwatch.tcss"
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("-", "go_to_parrent_dir", "Go to parrent dir"),
    ]
    background_color = None
    path = reactive(Path(os.getcwd()))

    def compose(self) -> ComposeResult:
        yield Header()
        yield DirectoryTree(self.path)
        yield Footer()

    def action_go_to_parrent_dir(self):
        self.path = self.path.parent

    def watch_path(self, new_path):
        try:
            self.query_one(DirectoryTree).remove()

            dt = DirectoryTree(new_path)

            self.mount(dt)
        except:
            print("Failed removing directory tree")

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )
    

if __name__ == "__main__":
    app = StopwatchApp()
    app.run()
