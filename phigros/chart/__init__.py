import typing as T


class BaseState:
    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} ' + ','.join(f'{k}={v}' for k, v in self.__dict__.items()) + '>'


class Line:
    class LineState(BaseState):
        sec: float
        x: float
        y: float
        angle: float
        width: float
        rev: bool

        def __init__(
                self,
                sec: float,
                x: float,
                y: float,
                angle: float,
                width: float,
                rev: bool
        ):
            self.sec = sec
            self.x = x
            self.y = y
            self.angle = angle
            self.width = width
            self.rev = rev

    notes: T.List['BaseNote']
    _states: T.List[LineState]

    def __init__(
            self,
            x: T.Optional[float] = 0,
            y: T.Optional[float] = 0.5,
            angle: T.Optional[float] = 0,
            width: T.Optional[float] = 1,
            rev: T.Optional[bool] = False
    ):
        from . import data
        self._states = []
        self._states.append(self.LineState(0, x, y, angle, width, rev))
        self.notes = []
        data.lines.append(self)

    def __repr__(self):
        return f'<{self.__class__.__name__} {self._states}'

    def __enter__(self) -> 'Line':
        from . import data
        self.prev_line = data.current_line
        data.current_line = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        from . import data
        data.current_line = self.prev_line

    def bind(self, note: 'BaseNote'):
        self.notes.append(note)

    def set(
            self,
            sec: float,
            *,
            x: T.Optional[float] = None,
            y: T.Optional[float] = None,
            angle: T.Optional[float] = None,
            width: T.Optional[float] = None,
            rev: T.Optional[bool] = None
    ) -> 'Line':
        if x is None:
            x = self._states[-1].x
        if y is None:
            y = self._states[-1].y
        if angle is None:
            angle = self._states[-1].angle
        if width is None:
            width = self._states[-1].width
        if rev is None:
            rev = self._states[-1].rev
        if sec == self._states[-1].sec:
            self._states[-1] = self.LineState(sec, x, y, angle, width, rev)
        else:
            self._states.append(self.LineState(sec, x, y, angle, width, rev))
        return self

    @property
    def states(self) -> T.List[LineState]:
        return self._states


class BaseNote:
    class NoteState(BaseState):
        sec: float
        pos: float
        speed: float

        def __init__(self, sec: float, pos: float, speed: float):
            self.sec = sec
            self.pos = pos
            self.speed = speed

    tap_sec: float
    show_sec: float
    _states: T.List[NoteState]

    def __init__(
            self,
            sec: float,
            pos: float,
            speed: float,
            line: T.Optional[Line] = None,
            show_sec: T.Optional[float] = -1
    ):
        from . import data
        if line is None:
            line = data.current_line
        if line is None:
            raise ValueError('Where is my line? :(')
        line.bind(self)
        self.tap_sec = sec
        self.show_sec = show_sec
        self._states = []
        self._states.append(self.NoteState(0, pos, speed))
        data.notes.append(self)
        if sec > data.latest:
            data.latest = sec

    def __repr__(self):
        return f'<{self.__class__.__name__} tap_sec={self.tap_sec},show_sec={self.show_sec},states={self._states}>'

    def set(
            self,
            sec: float,
            *,
            pos: T.Optional[float] = None,
            speed: T.Optional[float] = None
    ) -> 'BaseNote':
        if sec <= 0:
            sec += self.tap_sec
        if pos is None:
            pos = self._states[-1].pos
        if speed is None:
            speed = self._states[-1].speed
        if sec == self._states[-1].sec:
            self._states[-1] = self.NoteState(sec, pos, speed)
        else:
            self._states.append(self.NoteState(sec, pos, speed))
        return self

    @property
    def states(self) -> T.List[NoteState]:
        return self._states


class Click(BaseNote):
    pass


class Drag(BaseNote):
    pass


class Flick(BaseNote):
    pass


class Hold(BaseNote):
    end_sec: float

    def __init__(
            self,
            sec: float,
            pos: float,
            speed: float,
            duration: float,
            line: T.Optional[Line] = None,
            show_sec: T.Optional[float] = -1
    ):
        from . import data
        super().__init__(sec, pos, speed, line, show_sec)
        self.end_sec = sec + duration
        if self.end_sec > data.latest:
            data.latest = self.end_sec


from .group import *
from .helper import *
