import psutil
from textual.binding import Binding, BindingType
from typing import  ClassVar
from textual import work
from textual.widget import Widget
from textual.widgets import Static, DataTable

class ProcessManager(Widget):
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("k", "cursor_up", "Cursor up"),
        Binding("j", "cursor_down", "Cursor down"),
        Binding("d", "kill_process", "Kill proccess"),
    ]

    def __init__(self):
        super().__init__()
        self.cache = None

    def compose(self):
        yield DataTable()

    def on_mount(self):
        self.update_timer = self.set_interval(15, self.get_process_information, pause=True)

    def on_show(self):
        self.get_process_information()

    def on_focus(self):
        self.query_one(DataTable).focus()

    def stop_update(self):
        self.update_timer.pause()

    def resume_update(self):
        self.update_timer.resume()

    @work(thread=True)
    def get_process_information(self):
        dt = self.query_one(DataTable)
        
        COLUMNS = ["pid", "name", "username"]
        
        if not self.cache:
            dt.add_columns(*COLUMNS)

        current = {} 
        for process in psutil.process_iter(COLUMNS):
            info = process.info
            current[process.pid] = info

        if not self.cache:
            for info in current.values():
                row_values = [info[col] for col in COLUMNS]
                rk = dt.add_row(*row_values)
                info["row_key"] = rk
            self.cache = current
            return

        for pid, info in current.items():
            if pid not in self.cache:
                row_values = [info[col] for col in COLUMNS]
                rk = dt.add_row(*row_values)
                info["row_key"] = rk
            elif info != self.cache[pid]:
                info["row_key"] = self.cache[pid]["row_key"]
                for column in COLUMNS:
                    if info[column] != self.cache[pid][column]:
                        dt.update_cell(info["row_key"], column, info[column])

        for pid in list(self.cache.keys()):
            if pid not in current:
                dt.remove_row(self.cache[pid]["row_key"])

        self.cache = current
    
    def action_kill_process(self):
        dt = self.query_one(DataTable)
        pid = dt.get_row_at(dt.cursor_row)[0]
        try:
            pid_int = int(pid)
            proc = psutil.Process(pid_int)
            proc.kill()
            # Remove the row from the DataTable after killing the process
            row_key = dt._row_locations.get_key(dt.cursor_row)
            dt.remove_row(row_key)
        except (psutil.NoSuchProcess, ValueError, PermissionError):
            pass


        

    def action_cursor_down(self):
        self.query_one(DataTable).action_cursor_down()
    
    def action_cursor_up(self):
        self.query_one(DataTable).action_cursor_up()
