from phigros import *

spd = 0.5

with Line(4 / 6, 1 / 6) as line:
    Hold(1, 0, spd, 100)

# with Line(0, 5 / 6) as line:
#     Hold(2, 2 / 6, spd, 9)
#     for i in range(50, 100):
#         line.set(i / 50, y=1 - i / 50 / 6)
#
# with Line(3 / 6, 5 / 6) as line:
#     Hold(3, 0, spd, 8)
#     for i in range(50, 150):
#         line.set(i / 50, y=1 - i / 50 / 6)
#     for i in range(50, 451):
#         line.set(i / 50, angle=(i - 50) / 400 * 360)
#
# with Line(0, 5 / 6) as line:
#     Hold(4, 4 / 6, spd, 7)
#     for i in range(50, 200):
#         line.set(i / 50, y=1 - i / 50 / 6)
#
# with Line(0, 5 / 6) as line:
#     Hold(5, 5 / 6, spd, 6)
#     for i in range(50, 250):
#         line.set(i / 50, y=1 - i / 50 / 6)

preview()
