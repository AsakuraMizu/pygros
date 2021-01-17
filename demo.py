from json import dumps
from phigros import *

offset(10)
bpm(0, 222.22)

l = line(0, 114514, 0, 0)

with mul(144):
    with l:
        move(1, 2, 0.3, -0.3, sineIn, bounceOut)
        draw(0, """
f
h   t
h   t
d   t
""")

print(dumps(export(), indent=4))
