def chart(bpmList, judgeLineList, *, musicOffset = 0, timingBase = 48):
    for l in [bpmList, judgeLineList]:
        for i, o in enumerate(l):
            o['id'] = i
    return {
        'musicOffset': musicOffset,
        'timingBase': timingBase,
        'bpmList': bpmList,
        'judgeLineList': judgeLineList,
    }

c = chart

def bpm(time, bpm):
    return {
        'time': time,
        'bpm': bpm,
    }

b = bpm

def line(constructTime, destructTime, noteList, *, controlX = [], controlY = [], angle = [], speed = [], noteAlpha = [], lineAlpha = [], displayRange = []):
    for l in [noteList, controlX, controlY, angle, speed, noteAlpha, lineAlpha, displayRange]:
        for i, o in enumerate(l):
            o['id'] = i

    return {
        'constructTime': constructTime,
        'destructTime': destructTime,
        'noteList': noteList,
        'props': {
            'controlX': controlX,
            'controlY': controlY,
            'angle': angle,
            'speed': speed,
            'noteAlpha': noteAlpha,
            'lineAlpha': lineAlpha,
            'displayRange': displayRange,
        },
    }

l = line

easeInBack = 'easeInBack'
easeInBounce = 'easeInBounce'
easeInCirc = 'easeInCirc'
easeInCubic = 'easeInCubic'
easeInElastic = 'easeInElastic'
easeInExpo = 'easeInExpo'
easeInOutBack = 'easeInOutBack'
easeInOutBounce = 'easeInOutBounce'
easeInOutCirc = 'easeInOutCirc'
easeInOutCubic = 'easeInOutCubic'
easeInOutElastic = 'easeInOutElastic'
easeInOutExpo = 'easeInOutExpo'
easeInOutQuad = 'easeInOutQuad'
easeInOutQuart = 'easeInOutQuart'
easeInOutQuint = 'easeInOutQuint'
easeInOutSine = 'easeInOutSine'
easeInQuad = 'easeInQuad'
easeInQuart = 'easeInQuart'
easeInQuint = 'easeInQuint'
easeInSine = 'easeInSine'
easeOutBack = 'easeOutBack'
easeOutBounce = 'easeOutBounce'
easeOutCirc = 'easeOutCirc'
easeOutCubic = 'easeOutCubic'
easeOutElastic = 'easeOutElastic'
easeOutExpo = 'easeOutExpo'
easeOutQuad = 'easeOutQuad'
easeOutQuart = 'easeOutQuart'
easeOutQuint = 'easeOutQuint'
easeOutSine = 'easeOutSine'
linear = 'linear'
none = 'none'

def state(time, value, easing = none):
    return {
        'time': time,
        'value': value,
        'easing': easing,
    }

s = state

def note(type, time, holdTime, x, speed = 1, side = 1, isFake = False):
    return {
        'type': type,
        'time': time,
        'holdTime': holdTime,
        'x': x,
        'speed': speed,
        'side': side,
        'isFake': isFake,
    }

n = note

def tap(time, x, speed = 1, side = 1, isFake = False):
    return note(1, time, 0, x, speed, side, isFake)

t = tap

def drag(time, x, speed = 1, side = 1, isFake = False):
    return note(2, time, 0, x, speed, side, isFake)

d = drag

def hold(time, holdTime, x, speed = 1, side = 1, isFake = False):
    return note(3, time, holdTime, x, speed, side, isFake)

h = hold

def flick(time, x, speed = 1, side = 1, isFake = False):
    return note(4, time, 0, x, speed, side, isFake)

f = flick

def draw(time, drawing, *, d = 1, left = -1, right = 1, side = 1, speed = 1, isFake = False):
    lines = drawing.split('\n') if type(drawing) is str else drawing
    lines = [li for li in lines if not li == '']
    lines = list(reversed(lines))
    width = max([len(li) for li in lines])
    rtn = []
    holds = {}

    for i, li in enumerate(lines):
        for j, no in enumerate(li):
            dic = {
                't': tap,
                'f': flick,
                'F': flick,
                'd': drag,
                'D': drag,
            }
            if no in dic:
                rtn.append(dic[no](time + d * i, left + (right - left) / width * (j + 0.5), speed, side, isFake))
            if no == 'H':
                rtn.append(hold(time + d * i, time + d * i, left + (right - left) / width * (j + 0.5), speed, side, isFake))
            if no == 'h' or no == 'F' or no == 'D':
                if j not in holds:
                    holds[j] = i
            else:
                if j in holds:
                    rtn.append(hold(time + d * holds[j], time + d * i, left + (right - left) / width * (j + 0.5), speed, side, isFake))
                    holds.pop(j)

    for j in holds.keys():
        rtn.append(hold(time + d * holds[j], time + d * len(lines), left + (right - left) / width * (j + 0.5), speed, side, isFake))

    return rtn

dr = draw
