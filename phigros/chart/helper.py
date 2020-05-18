import typing as T

from . import BaseNote
from . import Hold


class BaseGroup:
    note_stack: T.List[BaseNote]
    latest: float

    def __enter__(self) -> 'BaseGroup':
        from . import data
        self.note_stack = data.note_stack
        self.latest = data.latest
        data.note_stack = []
        data.latest = 0
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        from . import data
        self.note_stack, data.note_stack = data.note_stack, [*self.note_stack, *data.note_stack]
        self.latest, data.latest = data.latest, max(self.latest, data.latest)


class Sub(BaseGroup):
    sec: float

    def __init__(self, sec: T.Optional[float] = None):
        from . import data
        if sec is None:
            sec = data.latest
        self.sec = sec

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(Sub, self).__exit__(exc_type, exc_val, exc_tb)
        for note in self.note_stack:
            for st in note.states:
                st.sec += self.sec
            note.show_sec += self.sec


class Group(BaseGroup):
    def set(
            self,
            sec: float,
            *,
            pos: T.Optional[float] = None,
            speed: T.Optional[float] = None,
            duration: T.Optional[float] = None
    ) -> 'Group':
        for note in self.note_stack:
            if isinstance(note, Hold):
                note.set(sec, pos=pos, speed=speed, duration=duration)
            else:
                note.set(sec, pos=pos, speed=speed)
        return self


def export():
    from . import data
    return data.note_stack, data.lines
