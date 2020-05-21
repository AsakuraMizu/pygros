import typing as T
from io import BytesIO

import cocos
import pyglet
from PIL import Image

from ..chart import Hold


def gen_animation(states: T.List[Hold.NoteState], tap_sec: float, end_sec: float):
    head = Image.open(pyglet.resource.file('holdhead.png'))
    body = Image.open(pyglet.resource.file('holdbody.png'))

    sec = tap_sec
    length = 0
    for i in states:
        if i.sec < tap_sec:
            continue
        length += i.speed * (i.sec - sec)
        sec = i.sec
    length += states[-1].speed * (end_sec - sec)
    res = Image.new('RGBA', (head.width, int(length)))
    res.paste(head, (0, int(length - head.height)))
    while length > 0:
        res.paste(body, (0, int(res.height - head.height - length)))
        length -= body.height
    frames: T.List[pyglet.image.AnimationFrame] = []
    with BytesIO() as f:
        res.save(f, format='png')
        frames.append(pyglet.image.AnimationFrame(pyglet.image.load('hold.png', f), tap_sec))
    fps = 30
    sec = tap_sec
    length = res.height
    for i in states:
        if i.sec < tap_sec:
            continue
        cnt = int((i.sec - sec) * fps)
        for _ in range(cnt):
            tmp = Image.new('RGBA', (res.width, res.height))
            tmp.paste(res.crop((0, 0, res.width, int(length))), (0, 0))
            with BytesIO() as f:
                tmp.save(f, format='png')
                frames.append(pyglet.image.AnimationFrame(pyglet.image.load('hold.png', f), 1 / fps))
            length -= i.speed / fps
        sec = i.sec
    passed = 0
    while passed < end_sec - sec:
        tmp = Image.new('RGBA', (res.width, res.height))
        tmp.paste(res.crop((0, 0, res.width, int(length))), (0, 0))
        with BytesIO() as f:
            tmp.save(f, format='png')
            frames.append(pyglet.image.AnimationFrame(pyglet.image.load('hold.png', f), 1 / fps))
        length -= 1.8 * states[-1].speed / fps
        passed += 1 / fps
    return pyglet.image.Animation(frames=frames)
