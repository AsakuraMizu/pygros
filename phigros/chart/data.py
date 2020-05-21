import typing as T

from . import BaseNote, Line

__all__ = ['notes', 'latest', 'current_line', 'lines']

latest: float = 0
current_line: T.Optional[Line] = None

notes: T.List[BaseNote] = []
lines: T.List[Line] = []
