import typing as T

from . import BaseNote, BaseState, Hold

__all__ = ['Multiplier', 'Group']


class BaseGroup:
    notes: T.List[BaseNote]
    states: T.List[BaseState]
    latest: float

    def __enter__(self) -> 'BaseGroup':
        from . import chart
        self.notes = chart.notes
        chart.notes = []
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        from . import chart
        self.notes, chart.notes = chart.notes, [*self.notes, *chart.notes]


class Multiplier(BaseGroup):
    mul: float

    def __init__(self, mul: T.Optional[float] = 1):
        self.mul = mul

    def __enter__(self):
        from . import data
        data.multiplier *= self.mul
        return super().__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)
        from . import data
        data.multiplier /= self.mul


class Group(BaseGroup):
    opened: bool
    states: T.List[T.Tuple[float, float, float]]

    def __init__(self):
        self.opened = False
        self.states = []

    def __enter__(self):
        super().__enter__()
        self.opened = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)
        self.opened = False
        for st in self.states:
            for note in self.notes:
                note.set(st[0], pos=st[1], speed=st[2])

    def set(
            self,
            sec: float,
            *,
            pos: T.Optional[float] = None,
            speed: T.Optional[float] = None
    ) -> 'Group':
        if self.opened:
            self.states.append((sec, pos, speed))
        else:
            for note in self.notes:
                note.set(sec, pos=pos, speed=speed)
        return self
