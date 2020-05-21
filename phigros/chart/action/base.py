class Action:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def init(self, *args, **kwargs):
        pass

    def serialize(self):
        return {'type': self.__class__.__name__.lower(), 'args': self.args, 'kwargs': self.kwargs}

    def __add__(self, other):



class Delay(Action):
    pass


class NoteAction(Action):
    pass


class LineAction(Action):
    pass
