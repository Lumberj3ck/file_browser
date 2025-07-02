import psutil
from textual.binding import Binding, BindingType
from typing import  ClassVar
from textual import work
from textual.widget import Widget
from textual.widgets import DataTable

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
        
        COLUMNS = [
            "pid", "name", "username", "cpu_percent", "memory_percent",
            "status", "num_threads", "ppid"
        ]
        
        if not self.cache:
            dt.add_columns(*COLUMNS)

        current = {} 
        for process in psutil.process_iter():
            try:
                info = process.as_dict(attrs=COLUMNS)
                # Format cpu_percent and memory_percent to 1 decimal place
                info["cpu_percent"] = f"{info.get('cpu_percent', 0):.1f}"
                info["memory_percent"] = f"{info.get('memory_percent', 0):.1f}"
                current[process.pid] = info
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        if not self.cache:
            for info in current.values():
                row_values = [info.get(col, "") for col in COLUMNS]
                rk = dt.add_row(*row_values)
                info["row_key"] = rk
            self.cache = current
            return

        new_cache = {}

        for pid, info in current.items():
            if pid in self.cache and "row_key" in self.cache[pid]:
                # Existing process, preserve row_key
                info["row_key"] = self.cache[pid]["row_key"]
                row_key = info["row_key"]
                for column in COLUMNS:
                    if (
                        row_key in dt._row_locations
                        and column in dt.columns
                        and info.get(column, "") != self.cache[pid].get(column, "")
                    ):
                        dt.update_cell(row_key, column, info.get(column, ""))
            else:
                # New process, add row
                row_values = [info.get(col, "") for col in COLUMNS]
                rk = dt.add_row(*row_values)
                info["row_key"] = rk
            new_cache[pid] = info

        # Remove rows for processes that have disappeared
        for pid in list(self.cache.keys()):
            if pid not in current:
                row_key = self.cache[pid]["row_key"]
                if row_key in dt._row_locations:
                    dt.remove_row(row_key)

        self.cache = new_cache
    
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
