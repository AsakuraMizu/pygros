from json import dumps
from phigros import *

data = c(
    [b(0, 100)],
    [
        l(
            0, 114514,
            [
                t(250, 0),
                *dr(500, [
                    'ffff'
                ])
            ],
            controlX=[s(0, 0)],
            controlY=[s(0, 0)],
            angle=[s(0, 0)],
            speed=[s(0, 0.005)],
            noteAlpha=[s(0, 1)],
            lineAlpha=[s(0, 1)],
            displayRange=[s(0, -1)],
        ),
    ],
)

print(dumps(data))
