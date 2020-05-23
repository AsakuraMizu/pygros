import typing as T

from . import BaseState, Line

current_line: T.Optional[Line] = None
offset: float = 0
multiplier: float = 1
