from time import monotonic
from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalScroll
from textual.widgets import Header, Digits, Button, Footer
from textual.reactive import reactive


class DisplayTime(Digits):
    """Will be used for displaying timer"""

    start_time = reactive(monotonic)
    time = reactive(0.0)
    total = reactive(0.0)

    def on_mount(self):
        self.update_timer = self.set_interval(1 / 60, self.update_time, pause=True)

    def update_time(self):
        self.time = self.total + monotonic() - self.start_time

    def watch_time(self, time):
        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(minutes, 60)
        self.update(f"{hours:02,.0f}:{minutes:02.0f}:{seconds:05.2f}")

    def start(self) -> None:
        self.start_time = monotonic()
        self.update_timer.resume()

    def stop(self) -> None:
        self.update_timer.pause()
        self.total += monotonic() - self.start_time
        self.time = self.total

    def reset(self):
        self.time = 0
        # self.start_time = 0
        self.total = 0


class Stopwatch(HorizontalGroup):

    def on_button_pressed(self, event):
        button_id = event.button.id
        time_display = self.query_one(DisplayTime)

        if button_id == "start":
            time_display.start()
            self.add_class("started")
        elif button_id == "stop":
            time_display.stop()
            self.remove_class("started")
        elif button_id == "reset":
            time_display.reset()

    def compose(self) -> ComposeResult:
        yield Button(label="Start", id="start", variant="success")
        yield Button(label="Stop", id="stop", variant="error")
        yield Button(label="Reset", id="reset")
        yield DisplayTime()


class StopwatchApp(App):
    CSS_PATH = "stopwatch.tcss"
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("a", "add_stopwatch", "Add"),
        ("r", "remove_stopwatch", "Remove"),
    ]
    background_color = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield VerticalScroll(Stopwatch(), id="timers")
        yield Footer()

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_add_stopwatch(self) -> None:
        new_stopwatch = Stopwatch()
        self.query_one("#timers").mount(new_stopwatch)
        new_stopwatch.scroll_visible()
    
    def action_remove_stopwatch(self) -> None:
        # queries exact element if we query #timers here we will get only one element
        # if we query Stopwatch we will get them
        timers = self.query(Stopwatch)
        if timers:
            timers.last().remove()


if __name__ == "__main__":
    app = StopwatchApp()
    app.run()
