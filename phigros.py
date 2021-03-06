from contextlib import contextmanager
from enum import Enum
from typing import Any, Dict, Generic, List, TypeVar, Union


__all__ = [
    'mul',
    'add',
    'linear',
    'jump',
    'backIn',
    'backOut',
    'bounceIn',
    'bounceOut',
    'circIn',
    'circOut',
    'cubicIn',
    'cubicOut',
    'elasticIn',
    'elasticOut',
    'expoIn',
    'expoOut',
    'quadIn',
    'quadOut',
    'quartIn',
    'quartOut',
    'sineIn',
    'sineOut',
    'construct',
    'move',
    'rotate',
    'fade',
    'speed',
    'notevis',
    'tap',
    'flick',
    'drag',
    'hold',
    'draw',
    'line',
    'offset',
    'bpm',
    'export',
]


T = TypeVar('T')


class HisVar(Generic[T]):
    _stack: List[T]

    def __init__(self, initial_value: T = None):
        self._stack = []
        if initial_value is not None:
            self.set(initial_value)

    def get(self) -> T:
        if len(self._stack) == 0:
            raise ValueError('No instance in history')
        return self._stack[-1]

    def set(self, v: T):
        self._stack.append(v)

    def revoke(self):
        self._stack.pop()


class Context:
    line: HisVar['Line'] = HisVar()
    timing = {
        'offset': 0.0,
        'bpmList': [],
    }
    lines: List['Line'] = []

    mul: HisVar[float] = HisVar(1.0)
    add: float = 0.0


ctx = Context()


def t(time: float) -> float:
    return time * ctx.mul.get() + ctx.add


@contextmanager
def mul(value: float):
    try:
        ctx.mul.set(ctx.mul.get() * value)
        yield
    finally:
        ctx.mul.set(ctx.mul.get() / value)


def add(value: float):
    ctx.add += ctx.mul.get() * value


Ease = str
linear = 'linear'
jump = 'jump'
backIn = 'backIn'
backOut = 'backOut'
bounceIn = 'bounceIn'
bounceOut = 'bounceOut'
circIn = 'circIn'
circOut = 'circOut'
cubicIn = 'cubicIn'
cubicOut = 'cubicOut'
elasticIn = 'elasticIn'
elasticOut = 'elasticOut'
expoIn = 'expoIn'
expoOut = 'expoOut'
quadIn = 'quadIn'
quadOut = 'quadOut'
quartIn = 'quartIn'
quartOut = 'quartOut'
sineIn = 'sineIn'
sineOut = 'sineOut'


class Event:
    type: str
    startTime: float
    endTime: float
    properties: Dict[str, Any]

    def __init__(self, type_: str, start_time: float, end_time: float, properties: Dict[str, Any]):
        self.type = type_
        self.startTime = t(start_time)
        self.endTime = t(end_time)
        self.properties = properties

        ctx.line.get().eventList.append(self)

    def export(self, id_: int):
        return {
            'id': id_,
            'type': self.type,
            'startTime': self.startTime,
            'endTime': self.endTime,
            'properties': self.properties,
        }


def construct(start_time: float, end_time: float, x: float, y: float, angle: float = 0,
              alpha: float = 1, spd: float = 1) -> Event:
    return Event('construct', start_time, end_time, {
        'x': x,
        'y': y,
        'angle': angle,
        'alpha': alpha,
        'speed': spd,
    })


def move(start_time: float, end_time: float, x: float, y: float, ease_x: Ease = linear,
         ease_y: Ease = linear) -> Event:
    return Event('move', start_time, end_time, {
        'x': x,
        'y': y,
        'easeX': ease_x,
        'easeY': ease_y,
    })


def rotate(start_time: float, end_time: float, angle: float, ease: Ease = linear) -> Event:
    return Event('rotate', start_time, end_time, {
        'angle': angle,
        'ease': ease,
    })


def fade(start_time: float, end_time: float, alpha: float, ease: Ease = linear) -> Event:
    return Event('fade', start_time, end_time, {
        'alpha': alpha,
        'ease': ease,
    })


def speed(start_time: float, end_time: float, spd: float, ease: Ease = jump) -> Event:
    return Event('speed', start_time, end_time, {
        'speed': spd,
        'ease': ease,
    })


def notevis(start_time: float, end_time: float, visibility: bool) -> Event:
    return Event('notevis', start_time, end_time, {
        'visibility': visibility,
    })


class Note:
    type: str
    startTime: float
    endTime: float
    relativeX: float
    side: int
    speed: float
    isFake: bool

    def __init__(self, type_: str, start_time: float, end_time: float, relative_x: float,
                 side: int, spd: float, is_fake: bool):
        self.type = type_
        self.startTime = t(start_time)
        self.endTime = t(end_time)
        self.relativeX = relative_x
        self.side = side
        self.speed = spd
        self.isFake = is_fake

        ctx.line.get().noteList.append(self)

    def export(self, id_: int):
        return {
            'id': id_,
            'type': self.type,
            'startTime': self.startTime,
            'endTime': self.endTime,
            'relativeX': self.relativeX,
            'side': self.side,
            'speed': self.speed,
            'isFake': self.isFake,
        }


def tap(time: float, relative_x: float, *, side: int = 1, spd: float = 1, is_fake: bool = False) -> Note:
    return Note('tap', time, time, relative_x, side, spd, is_fake)


def flick(time: float, relative_x: float, *, side: int = 1, spd: float = 1, is_fake: bool = False) -> Note:
    return Note('flick', time, time, relative_x, side, spd, is_fake)


def drag(time: float, relative_x: float, *, side: int = 1, spd: float = 1, is_fake: bool = False) -> Note:
    return Note('drag', time, time, relative_x, side, spd, is_fake)


def hold(start_time: float, end_time: float, relative_x: float, *, side: int = 1, spd: float = 1,
         is_fake: bool = False) -> Note:
    return Note('hold', start_time, end_time, relative_x, side, spd, is_fake)


def draw(time: float, drawing: Union[List[str], str], *, d: int = 1, left: int = -1, right: int = 1,
         side: int = 1, spd: float = 1, is_fake: bool = False) -> List[Note]:
    lines: List[str] = drawing.split('\n') if type(drawing) is str else drawing
    lines = [li for li in lines if not li == '']
    lines = list(reversed(lines))
    width = max([len(li) for li in lines])
    rtn: List[Note] = []
    holds: Dict[int, int] = {}

    for i, li in enumerate(lines):
        for j, no in enumerate(li):
            dic = {
                't': tap,
                'f': flick,
                'F': flick,
                'd': drag,
                'D': drag,
            }
            if no in dic:
                dic[no](time + d * i, left + (right - left) / width * (j + 0.5), side=side, spd=spd, is_fake=is_fake)
            if no == 'H':
                hold(time + d * i, time + d * i, left + (right - left) / width * (j + 0.5),
                     side=side, spd=spd, is_fake=is_fake)
            if no == 'h' or no == 'F' or no == 'D':
                if j not in holds:
                    holds[j] = i
            else:
                if j in holds:
                    hold(time + d * holds[j], time + d * i, left + (right - left) / width * (j + 0.5),
                         side=side, spd=spd, is_fake=is_fake)
                    holds.pop(j)

    for j in holds.keys():
        hold(time + d * holds[j], time + d * len(lines), left + (right - left) / width * (j + 0.5),
             side=side, spd=spd, is_fake=is_fake)

    return rtn


class Line:
    eventList: List[Event] = []
    noteList: List[Note] = []

    def __init__(self):
        ctx.lines.append(self)

    def __enter__(self) -> 'Line':
        ctx.line.set(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        ctx.line.revoke()

    def export(self, id_: int):
        return {
            'id': id_,
            'eventList': [e.export(i) for i, e in enumerate(self.eventList)],
            'noteList': [n.export(i) for i, n in enumerate(self.noteList)],
        }


def line(start_time: float, end_time: float, x: float, y: float, angle: float = 0,
         alpha: float = 1, spd: float = 1) -> Line:
    rtn = Line()
    with rtn:
        construct(start_time, end_time, x, y, angle, alpha, spd)
    return rtn


def offset(offset_: float):
    ctx.timing['offset'] = offset_


def bpm(time: float, bpm_: float):
    ctx.timing['bpmList'].append({
        'time': time,
        'bpm': bpm_,
    })


def export():
    chart = {
        'timing': {
            'offset': ctx.timing['offset'],
            'bpmList': [{'id': i, **b} for i, b in enumerate(ctx.timing['bpmList'])]
        },
        'judgeLineList': [li.export(i) for i, li in enumerate(ctx.lines)],
    }

    return chart
