import typing as T

from . import BaseNote, Line

__all__ = ['notes', 'lines']

notes: T.List[BaseNote] = []
lines: T.List[Line] = []
