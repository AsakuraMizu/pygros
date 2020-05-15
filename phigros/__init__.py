import typing as T

_note_stack: T.List['BaseNote'] = []
_latest: float = 0

_lines: T.List['Line'] = []
_line: T.Optional['Line'] = None


class BaseState:
    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} ' + ','.join(f'{k}={v}' for k, v in self.__dict__.items()) + '>'


class Line:
    class LineState(BaseState):
        sec: float
        x: float
        y: float
        rx: float
        ry: float
        width: float
        rev: bool

        def __init__(
                self,
                sec: float,
                x: float,
                y: float,
                rx: float,
                ry: float,
                width: float,
                rev: bool
        ):
            self.sec = sec
            self.x = x
            self.y = y
            self.rx = rx
            self.ry = ry
            self.width = width
            self.rev = rev

    _notes: T.List['BaseNote']
    _note_stack: T.List[LineState]

    def __init__(
            self,
            x: T.Optional[float] = 0,
            y: T.Optional[float] = 0.5,
            rx: T.Optional[float] = 1,
            ry: T.Optional[float] = 0,
            width: T.Optional[float] = 1,
            rev: T.Optional[bool] = False
    ):
        self._stack = []
        self._stack.append(self.LineState(0, x, y, rx, ry, width, rev))
        self._notes = []
        _lines.append(self)

    def __repr__(self):
        return f'<{self.__class__.__name__} {self._stack}'

    def __enter__(self) -> 'Line':
        global _line
        _line = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        global _line
        _line = None

    def bind(self, note: 'BaseNote'):
        self._notes.append(note)

    def set(
            self,
            sec: float,
            *,
            x: T.Optional[float] = None,
            y: T.Optional[float] = None,
            rx: T.Optional[float] = None,
            ry: T.Optional[float] = None,
            width: T.Optional[float] = None,
            rev: T.Optional[bool] = None
    ) -> 'Line':
        if x is None:
            x = self._stack[-1].x
        if y is None:
            y = self._stack[-1].y
        if rx is None:
            rx = self._stack[-1].rx
        if ry is None:
            ry = self._stack[-1].ry
        if width is None:
            width = self._stack[-1].width
        if rev is None:
            rev = self._stack[-1].rev
        if sec == self._stack[-1].sec:
            self._stack[-1] = self.LineState(sec, x, y, rx, ry, width, rev)
        else:
            self._stack.append(self.LineState(sec, x, y, rx, ry, width, rev))
        return self

    @property
    def states(self) -> T.List[LineState]:
        return self._stack


class BaseNote:
    class NoteState(BaseState):
        sec: float
        x: float
        y: float
        speed: float

        def __init__(self, sec: float, x: float, y: float, speed: float):
            self.sec = sec
            self.x = x
            self.y = y
            self.speed = speed

    line: Line
    show_sec: float
    _stack: T.List[NoteState]

    def __init__(
            self,
            sec: float,
            x: float,
            y: float,
            speed: float,
            line: T.Optional[Line] = None,
            show_sec: T.Optional[float] = -1,
            prevent_default: T.Optional[bool] = False
    ):
        if line is None:
            line = _line
        if line is None:
            raise ValueError('Where is my line? :(')
        self.line = line
        line.bind(self)
        self.show_sec = show_sec
        self._stack = []
        if not prevent_default:
            self._stack.append(self.NoteState(sec, x, y, speed))
        _note_stack.append(self)
        global _latest
        if sec > _latest:
            _latest = sec

    def __repr__(self):
        return f'<{self.__class__.__name__} {self._stack}>'

    def set(
            self,
            sec: float,
            *,
            x: T.Optional[float] = None,
            y: T.Optional[float] = None,
            speed: T.Optional[float] = None
    ) -> 'BaseNote':
        if sec <= 0:
            sec += self._stack[0].sec
        if x is None:
            x = self._stack[-1].x
        if y is None:
            y = self._stack[-1].y
        if speed is None:
            speed = self._stack[-1].speed
        if sec == self._stack[-1].sec:
            self._stack[-1] = self.NoteState(sec, x, y, speed)
        else:
            self._stack.append(self.NoteState(sec, x, y, speed))
        return self

    @property
    def states(self) -> T.List[NoteState]:
        return self._stack


class Click(BaseNote):
    pass


class Drag(BaseNote):
    pass


class Flick(BaseNote):
    pass


class Hold(BaseNote):
    class HoldNoteState(BaseNote.NoteState):
        duration: float

        def __init__(self, sec: float, x: float, y: float, speed: float, duration: float):
            super().__init__(sec, x, y, speed)
            self.duration = duration

    _stack: T.List[HoldNoteState]

    def __init__(
            self,
            sec: float,
            x: float,
            y: float,
            speed: float,
            duration: float,
            line: T.Optional[Line] = None,
            show_sec: T.Optional[float] = -1
    ):
        super().__init__(sec, x, y, speed, line, show_sec, True)
        self._stack.append(self.HoldNoteState(sec, x, y, speed, duration))
        global _latest
        if sec + duration > _latest:
            _latest = sec + duration

    def set(
            self,
            sec: float,
            *,
            x: T.Optional[float] = None,
            y: T.Optional[float] = None,
            speed: T.Optional[float] = None,
            duration: T.Optional[float] = None
    ) -> 'Hold':
        if sec <= 0:
            sec += self._stack[0].sec
        if x is None:
            x = self._stack[-1].x
        if y is None:
            y = self._stack[-1].y
        if speed is None:
            speed = self._stack[-1].speed
        if duration is None:
            duration = self._stack[-1].duration
        if sec == self._stack[-1].sec:
            self._stack[-1] = self.HoldNoteState(sec, x, y, speed, duration)
        else:
            self._stack.append(self.HoldNoteState(sec, x, y, speed, duration))
        return self


class Empty(BaseNote):
    def __init__(self, length: float):
        super().__init__(_latest + length, 0, 0, 0)


class BaseGroup:
    _note_stack: T.List[BaseNote]
    _latest: float

    def __enter__(self) -> 'BaseGroup':
        global _note_stack, _latest
        self._stack = _note_stack
        self._latest = _latest
        _note_stack = []
        _latest = 0
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        global _note_stack, _latest
        self._stack, _note_stack = _note_stack, [*self._stack, *_note_stack]
        self._latest, _latest = _latest, max(self._latest, _latest)


class Sub(BaseGroup):
    sec: float

    def __init__(self, sec: T.Optional[float] = None):
        if sec is None:
            sec = _latest
        self.sec = sec

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(Sub, self).__exit__(exc_type, exc_val, exc_tb)
        for note in self._stack:
            if isinstance(note, Empty):
                continue
            for st in note.states:
                st.sec += self.sec
            note.show_sec += self.sec
        global _latest


# TODO
# class Group(BaseGroup):
#     class GroupState(BaseNote.NoteState):
#         pass

# This export function are just for testing
# Will be rewritten in the future
def export():
    return {'notes': _note_stack, 'lines': _lines}
