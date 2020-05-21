import copy
import typing as T
from os import path

import cocos
import cocos.batch
import cocos.actions as cac
import pyglet

from ..chart import Line, BaseNote, Drag, Flick, Hold, data

__all__ = ['preview']
_size = 0


class NoteExplode(cocos.sprite.Sprite):
    def __init__(self, pos):
        super().__init__('explode.png', pos, 0, 1 / 7)
        self.do(cac.ScaleBy(1.2, 0.2) + cac.Delay(0.2) + cac.FadeOut(0.1) + cac.CallFuncS(lambda e: e.kill()))


class NoteSprite(cocos.sprite.Sprite):
    def __init__(self, note: BaseNote):
        def p(state: BaseNote.NoteState):
            res = copy.copy(state)
            res.pos *= _size
            res.speed *= _size
            return res

        states = list(map(p, sorted(note.states, key=lambda e: e.sec)))
        dis = 0
        sec = note.tap_sec
        for i in states[::-1]:
            dis += (sec - i.sec) * i.speed
            sec = i.sec
        dis += sec * states[0].speed
        img = 'click.png'
        if isinstance(note, Drag):
            img = 'drag.png'
        elif isinstance(note, Flick):
            img = 'flick.png'
        elif isinstance(note, Hold):
            from .hold import gen_animation
            img = gen_animation(states, note.tap_sec, note.end_sec)
            dis += img.frames[0].image.height // 2
        super().__init__(img, (states[0].pos, dis), 0)
        sec = 0
        speed = states[0].speed
        action = None
        for i in states:
            dis -= (i.sec - sec) * speed
            if not action:
                action = cac.MoveTo((i.pos, dis), i.sec - sec)
            else:
                action += cac.MoveTo((i.pos, dis), i.sec - sec)
            sec = i.sec
            speed = i.speed
        action += cac.MoveTo((states[-1].pos, img.frames[0].image.height // 2 if isinstance(note, Hold) else 0),
                             note.tap_sec - sec)
        if isinstance(note, Hold):
            action += cac.MoveTo((states[-1].pos, -img.frames[0].image.height // 2), note.end_sec - note.tap_sec)

        def explode(e: NoteSprite):
            e.kill()
            e.parent.add(NoteExplode((e.x, e.y + img.frames[0].image.height // 2 if isinstance(note, Hold) else 0)))

        action += cac.CallFuncS(explode)
        self.do(action)


class LineSprite(cocos.sprite.Sprite):
    def __init__(self, line: Line):
        def p(state: Line.LineState):
            res = copy.copy(state)
            res.x *= _size
            res.y *= _size
            return res

        states = list(map(p, sorted(line.states, key=lambda e: e.sec)))
        super().__init__('line.png', (states[0].x, states[0].y), states[0].angle)
        for note in line.notes:
            self.add(NoteSprite(note))
        action = None
        pre = states[0]
        for i in states[1:]:
            if not action:
                action = cac.MoveTo((i.x, i.y), i.sec - pre.sec) | cac.RotateBy(i.angle - pre.angle, i.sec - pre.sec)
            else:
                action += cac.MoveTo((i.x, i.y), i.sec - pre.sec) | cac.RotateBy(i.angle - pre.angle, i.sec - pre.sec)
            pre = i
        if action:
            self.do(action)


class Player(cocos.layer.Layer):
    def __init__(self):
        super().__init__()
        # batch = cocos.batch.BatchNode()
        # self.add(batch)
        for line in data.lines:
            self.add(LineSprite(line))


def preview(size=480):
    global _size
    _size = size
    pyglet.resource.path.extend([path.join(path.dirname(__file__), 'resources')])
    pyglet.resource.reindex()
    cocos.director.director.init()
    main_scene = cocos.scene.Scene(Player())
    cocos.director.director.run(main_scene)
