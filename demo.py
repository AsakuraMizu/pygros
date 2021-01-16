from json import dumps
from phigros import *

offset(10)
bpm(0, 222.22)
bpm(10, 222.22)
bpm(20, 222.22)

l = line(0, 114514, 0, 0)

with l:
    tap(5, 0)

print(dumps(export(), indent=4))
