from datetime import datetime
from pathlib import Path

class SessionReport:
    TIME_FMT = "%d.%m.%Y %H:%M:%S"

    def __init__(self, login: str, time_in: datetime) -> None:
        self._login = login
        self._time_in = time_in
        self._time_out: datetime | None = None

    @property
    def login(self) -> str:
        return self._login

    @login.setter
    def login(self, value: str) -> None:
        self._login = value.strip()

    def close(self, time_out: datetime | None = None) -> Path:
        self._time_out = time_out or datetime.now()
        path = Path("session_report.txt")
        path.write_text(self.render(), encoding="utf-8")
        return path

    def render(self) -> str:
        tin = self._time_in.strftime(self.TIME_FMT)
        tout = (self._time_out or datetime.now()).strftime(self.TIME_FMT)
        login = self._login[:20]
        w_login, w_in, w_out = 20, 19, 19
        line = f"+-{'-' * w_login}-+-{'-' * w_in}-+-{'-' * w_out}-+"
        header = (
            f"| {'login':<{w_login}} | {'time_in':<{w_in}} | {'time_out':<{w_out}} |"
        )
        row = f"| {login:<{w_login}} | {tin:<{w_in}} | {tout:<{w_out}} |"
        return "\n".join([line, header, line.replace("-", "-"), row, line]) + "\n"