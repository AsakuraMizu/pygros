import copy
from os import path, stat

import cocos
import cocos.actions
import cocos.sprite
import cocos.layer

import pyglet

from . import data, settings
from ..chart import Line, BaseNote, Drag, Flick, Hold, chart

__all__ = ['preview']

combo_label = None
score_label = None

def update_labels():
    global combo_label, score_label

    parent = None
    if combo_label is not None:
        parent = combo_label.parent
        combo_label.kill()
    if data.combo > 2:
        text = str(data.combo)
    else:
        text = ''
    combo_label = cocos.text.Label(text, (settings.width / 2, settings.height),
                                   font_name=settings.font_name, font_size=20,
                                   anchor_x='center', anchor_y='top')
    combo_label.add(cocos.text.Label('AUTOPLAY' if data.combo > 2 else '', (0, -30),
                                     font_name=settings.font_name, font_size=10,
                                     anchor_x='center', anchor_y='top'))
    if parent is not None:
        parent.add(combo_label)

    parent = None
    if score_label is not None:
        parent = score_label.parent
        score_label.kill()
    text = str(round(data.score)).zfill(7)
    score_label = cocos.text.Label(text,
                                   (min(settings.width, (settings.width + settings.size) / 2), settings.height),
                                   font_name=settings.font_name, font_size=15,
                                   anchor_x='right', anchor_y='top')
    if parent is not None:
        parent.add(score_label)


def score():
    data.combo += 1
    data.score += 1000000 / data.all_combo
    update_labels()


class NoteExplode(cocos.sprite.Sprite):
    def __init__(self, pos):
        images=[pyglet.resource.image('Explode-1_1.png'),
                pyglet.resource.image('Explode-1_2.png'),
                pyglet.resource.image('Explode-1_3.png'),
                pyglet.resource.image('Explode-1_4.png'),
                pyglet.resource.image('Explode-1_5.png'),
                pyglet.resource.image('Explode-1_6.png'),
                pyglet.resource.image('Explode-1_7.png'),
                pyglet.resource.image('Explode-1_8.png'),
                pyglet.resource.image('Explode-1_9.png'),
                pyglet.resource.image('Explode-1_10.png'),
                pyglet.resource.image('Explode-1_11.png'),
                pyglet.resource.image('Explode-1_12.png'),
                pyglet.resource.image('Explode-1_13.png'),
                pyglet.resource.image('Explode-1_14.png'),
                pyglet.resource.image('Explode-1_15.png'),
                pyglet.resource.image('Explode-1_16.png'),
                pyglet.resource.image('Explode-1_17.png'),
                pyglet.resource.image('Explode-1_18.png'),
                pyglet.resource.image('Explode-1_19.png'),
                pyglet.resource.image('Explode-1_20.png'),
                pyglet.resource.image('Explode-1_21.png'),
                pyglet.resource.image('Explode-1_22.png'),
                pyglet.resource.image('Explode-1_23.png'),
                pyglet.resource.image('Explode-1_24.png'),
                pyglet.resource.image('Explode-1_25.png'),
                pyglet.resource.image('Explode-1_26.png'),
                pyglet.resource.image('Explode-1_27.png'),
                pyglet.resource.image('Explode-1_28.png'),
                pyglet.resource.image('Explode-1_29.png')]
        ani = pyglet.image.Animation.from_image_sequence(images, duration=0.01, loop=False)
        super().__init__(ani, pos)
        self.do(cocos.actions.ScaleBy(1.3, 0.1) + cocos.actions.Delay(0.05) + cocos.actions.FadeOut(0.05) + cocos.actions.CallFuncS(lambda e: e.kill()))


class NoteSprite(cocos.sprite.Sprite):
    def __init__(self, note: BaseNote):
        def play_sound():
            sound = 'click.wav'
            if isinstance(note, Drag):
                sound = 'drag.wav'
            elif isinstance(note, Flick):
                sound = 'flick.wav'
            return pyglet.resource.media(sound).play()
        def p(state: BaseNote.NoteState):
            res = copy.copy(state)
            res.pos *= settings.size
            res.speed *= settings.size
            return res
        note.states.sort(key=lambda e:e.sec)
        for state in note.states:
            state.pos *=settings.size
            state.speed *=settings.size
        states = note.states
        dis = 0
        img = 'tap.png'
        if isinstance(note, Drag):
            img = 'drag.png'
        elif isinstance(note, Flick):
            img = 'flick.png'
        elif isinstance(note, Hold):
            img = 'hold.png'
            sec = note.tap_sec
            length = 0
            for i in states:
                if i.sec <= note.tap_sec:
                    continue
                length += i.speed * (i.sec - sec)
                sec = i.sec
            length += states[-1].speed * (note.end_sec - sec)
            dis += length // 2
        sec = note.tap_sec
        for i in states[::-1]:
            if i.sec > note.tap_sec:
                break
            note.show_sec = min(
                note.show_sec,
                sec - (settings.size * 2 - abs(dis) + (length if isinstance(note, Hold) else 0)) / abs(i.speed)
            )
            dis += (sec - i.sec) * i.speed
            sec = i.sec
        note.show_sec = min(
            note.show_sec,
            sec - (settings.size * 2 - abs(dis) + (length if isinstance(note, Hold) else 0)) / abs(states[0].speed)
        )
        dis += sec * states[0].speed
        super().__init__(img, (states[0].pos, dis))
        if isinstance(note, Hold):
            self.scale_y = length / self.image.height
        action = cocos.actions.Hide()
        sec = 0
        speed = states[0].speed
        for i in states:
            if i.sec > note.tap_sec:
                break
            dis -= (i.sec - sec) * speed
            act = cocos.actions.MoveTo((i.pos, dis), i.sec - sec)
            if sec <= note.show_sec < i.sec:
                act |= cocos.actions.Delay(note.show_sec - sec) + cocos.actions.Show()
            action += act
            sec = i.sec
            speed = i.speed
        act = cocos.actions.MoveTo((states[-1].pos, length // 2 if isinstance(note, Hold) else 0), note.tap_sec - sec)
        if sec <= note.show_sec < note.tap_sec:
            act |= cocos.actions.Delay(note.show_sec - sec) + cocos.actions.Show()
        action += act
        action += cocos.actions.CallFunc(play_sound)

        if isinstance(note, Hold):
            class Qwq(cocos.actions.IntervalAction):
                def init(self, length, duration):
                    self._length = length
                    self.duration = duration

                def start(self):
                    self._cur = self.target.scale_y

                def update(self, t):
                    from random import randint
                    if randint(0, 6) < 3:
                        self.target.parent.add(NoteExplode((self.target.x, 0)))
                    self.target.scale_y = (self._cur - self._length) * (1 - t) + self._length

            nowlen = length // 2
            sec = note.tap_sec
            for i in states:
                if i.sec <= note.tap_sec:
                    continue
                nowlen -= (i.sec - sec) * i.speed
                action += cocos.actions.MoveTo((states[-1].pos, nowlen // 2), i.sec - sec) | \
                          Qwq(nowlen / self.image.height, i.sec - sec)
                sec = i.sec
            action += cocos.actions.MoveTo((states[-1].pos, 0), note.end_sec - sec) | \
                      Qwq(0, note.end_sec - sec)

        def explode(e: NoteSprite):
            e.kill()
            e.parent.add(NoteExplode((e.x, e.y)))
            score()

        action += cocos.actions.CallFuncS(explode)
        self.do(action)


class LineSprite(cocos.sprite.Sprite):
    def __init__(self, line: Line):
        class width_adjustment(cocos.actions.IntervalAction):
            def init(self, width, duration):
                self._width = width
                self.duration = duration

            def start(self):
                self._cur = self.target.scale_y

            def update(self, t):
                self.target.scale_y = (self._cur - self._width) * (1 - t) + self._width
        line.states.sort(key=lambda e:e.sec)
        for state in line.states:
            state.x*=settings.size
            state.x += (settings.width - settings.size) / 2
            state.y *= settings.size
            state.y += (settings.height - settings.size) / 2
        states = line.states
        super().__init__('line_empty.png', (states[0].x, states[0].y), states[0].angle)
        line_sprite = cocos.sprite.Sprite('line.png')
        self.add(line_sprite)
        for note in line.notes:
            self.add(NoteSprite(note))
        action = None
        pre = states[0]
        for i in states[1:]:
            act = cocos.actions.MoveTo((i.x, i.y), i.sec - pre.sec) | cocos.actions.RotateBy(i.angle - pre.angle, i.sec - pre.sec)
            if i.rev != pre.rev:
                act |= cocos.actions.Delay(i.sec - pre.sec) + cocos.actions.FlipY(duration=0.01)
            if not action:
                action = act
            else:
                action += act
            pre = i
        if action:
            self.do(action)
        action = None
        sec = 0
        for i in states:
            act = width_adjustment(i.width, i.sec - sec)
            if not action:
                action = act
            else:
                action += act
            sec = i.sec
        if action:
            line_sprite.do(action)


class Player(cocos.layer.Layer):
    def __init__(self):
        super().__init__()
        if settings.background is not None:
            back = cocos.sprite.Sprite(settings.background, (settings.width / 2, settings.height / 2))
            back.opacity = settings.opacity
            back.scale = settings.height / back.image.height
            self.add(back)
        for line in chart.lines:
            self.add(LineSprite(line))
        update_labels()
        self.add(combo_label)
        self.add(score_label)
        self.add(cocos.text.Label(settings.name,
                                  (max(0, (settings.width - settings.size) / 2), 0),
                                  font_name=settings.font_name, font_size=15,
                                  anchor_x='left', anchor_y='bottom'))
        self.add(cocos.text.Label(settings.diff,
                                  (min(settings.width, (settings.width + settings.size) / 2), 0),
                                  font_name=settings.font_name, font_size=15,
                                  anchor_x='right', anchor_y='bottom'))
        if settings.music is not None:
            pyglet.resource.media(settings.music).play()


def preview(
        name='test',
        diff='SP Lv ?',
        music=None,
        background=None,
        *,
        height=600,
        width=800,
        size=600,
        opacity=127,
        font_name=['Electrolize'],
):
    settings.name = name
    settings.diff = diff
    settings.music = music
    settings.background = background
    settings.height = height
    settings.width = width
    settings.size = size
    settings.opacity = opacity
    settings.font_name = font_name
    data.all_combo = len(chart.notes)
    pyglet.resource.path.extend([path.join(path.dirname(__file__), 'resources')])
    pyglet.resource.reindex()
    pyglet.resource.add_font('Electrolize.ttf')
    cocos.director.director.init(width=width, height=height)
    main_scene = cocos.scene.Scene(Player())
    cocos.director.director.run(main_scene)
