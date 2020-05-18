import typing as T

from . import BaseNote, Line

__all__ = ['note_stack', 'latest', 'line', 'lines']

note_stack: T.List[BaseNote] = []
latest: float = 0
line: T.Optional[Line] = None
lines: T.List[Line] = []
