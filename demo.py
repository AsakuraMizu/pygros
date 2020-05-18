from phigros import *

bpm = 128

line = Line(0, 1, 0, 1)
with line:
    Click(1, 2, bpm)
line.set(0.2, rev=True)
with Line(1, 1, 1):
    with Sub():
        group = Group()
        with group:
            Click(0.5, 1, bpm)
            Click(1, 1, bpm).set(-1, speed=bpm / 2)
        group.set(0.4, speed=bpm * 10)
        with Sub(2):
            Hold(2, 2, bpm * 2, 0).set(-1, duration=1).set(-1, pos=1)
            Flick(3, 3, bpm)

print(export())
