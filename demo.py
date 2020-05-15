from phigros import *

bpm = 128

with Sub():
    line = Line(0, 1, 0, 1)
    with line:
        Click(0, 2, 1, bpm)
    line.set(0.2, rev=True)
    with Line(1, 1, 1, 1):
        Click(0.5, 1, 1, bpm)
        Click(1, 1, 2, bpm).set(-1, speed=bpm / 2)
        Empty(1)
        with Sub():
            Hold(2, 2, 2, bpm * 2, 0).set(-1, duration=1).set(-1, x=1)
            Flick(3, 3, 3, bpm)

print(export())
