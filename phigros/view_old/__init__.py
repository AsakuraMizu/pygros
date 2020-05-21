from io import BytesIO

import pygame

from ..chart import Click, Drag, Flick, data
from ..resource import get_res

__all__ = ['preview']

_size = 0


def scale(pos):
    return pos[0] * _size, pos[1] * _size


class LineSprite(pygame.sprite.Sprite):
    def __init__(self, line):
        super().__init__()
        self.states = sorted(line.states, key=lambda e: e.sec)
        self.center = scale((self.states[0].x, self.states[0].y))
        self.angle = self.states[0].angle
        self.master_image = pygame.image.load(BytesIO(get_res('line')), 'line.png').convert_alpha()
        self.image = pygame.transform.rotate(self.master_image, self.angle)
        self.rect = self.image.get_rect(center=self.center)

    def update(self, current_sec):
        if not len(self.states):
            return
        while len(self.states) and current_sec >= self.states[0].sec:
            self.states.pop(0)
            if not len(self.states):
                return
            self.center = scale((self.states[0].x, self.states[0].y))
            self.angle = self.states[0].angle
            self.image = pygame.transform.rotate(self.master_image, self.angle)
            self.rect = self.image.get_rect(center=self.center)


class BaseNoteExplode(pygame.sprite.Sprite):
    def __init__(self, sec, center):
        super().__init__()
        self.center = center
        self.master_image = pygame.image.load(BytesIO(get_res('explode')), 'explode.png').convert_alpha()
        self.image = pygame.transform.scale(self.master_image, (0, 0))
        self.rect = self.image.get_rect(center=center)
        self.sec = sec

    def update(self, current_sec):
        if current_sec < self.sec:
            return
        if current_sec - self.sec <= 0.2:
            size = 100 + int((current_sec - self.sec) * 200)
            self.image = pygame.transform.scale(self.master_image, (size, size))
            self.rect = self.image.get_rect(center=self.center)
        elif current_sec - self.sec < 0.8:
            pass
        else:
            self.kill()


class BaseNoteSprite(pygame.sprite.Sprite):
    def __init__(self, note, line, type_):
        super().__init__()
        self.line = line
        self.tap_sec = note.tap_sec
        self.show_sec = note.show_sec
        self.states = sorted(note.states, key=lambda e: e.sec)
        self.pos = _size * self.states[0].pos
        self.speed = _size * self.states[0].speed
        dis = 0
        sec = self.tap_sec
        for i in self.states[::-1]:
            dis += (sec - i.sec) * _size * i.speed
            sec = i.sec
        self.dis = dis
        self.last_sec = 0
        self.center = (0, 0)
        self.master_image = pygame.image.load(BytesIO(get_res(type_)), f'{type_}.png')
        self.image = self.master_image
        self.rect = self.image.get_rect(size=(0, 0))

    def update(self, current_sec):
        while len(self.states) and current_sec >= self.states[0].sec:
            self.pos = _size * self.states[0].pos
            self.speed = _size * self.states[0].speed
            self.states.pop(0)
        self.dis -= (current_sec - self.last_sec) * self.speed
        vec1 = pygame.Vector2()
        vec1.from_polar((self.pos, -self.line.angle))
        if vec1.length_squared() == 0:
            vec2 = pygame.Vector2()
            vec2.from_polar((self.dis, -self.line.angle - 90))
        else:
            vec2 = vec1.rotate(-90 if self.pos > 0 else 90)
            vec2.scale_to_length(self.dis)
        self.center = vec1 + vec2 + self.line.center
        self.image = pygame.transform.rotate(self.master_image, self.line.angle)
        self.rect = self.image.get_rect(center=self.center)
        self.last_sec = current_sec
        if current_sec >= self.tap_sec:
            exp = BaseNoteExplode(current_sec, self.center)
            for group in self.groups():
                group.add(exp)
            self.kill()
            return


class HoldSprite(BaseNoteSprite):
    def __init__(self, note, line):
        super().__init__(note, line, 'hold')
        self.duration = self.states[0].duration
        self.master_height = self.master_image.get_rect().height // 3
        self.master_width = self.master_image.get_rect().width
        self.start_image = self.master_image.subsurface(
            self.master_image.get_rect(top=self.master_height * 2, height=self.master_height))
        self.end_image = self.master_image.subsurface(self.master_image.get_rect(height=self.master_height))
        self.master_mid_image = self.master_image.subsurface(
            self.master_image.get_rect(top=self.master_height, height=self.master_height))
        self.mid_image = pygame.transform.scale(self.master_mid_image, (0, 0))
        self.tmp_image = self.image

    def update(self, current_sec):
        while len(self.states) and current_sec >= self.states[0].sec:
            self.pos = _size * self.states[0].pos
            self.speed = _size * self.states[0].speed
            self.duration = self.states[0].duration
            self.mid_image = pygame.transform.scale(self.master_mid_image,
                                                    (self.master_width, int(abs(self.duration * self.speed))))
            self.tmp_image = pygame.Surface(
                (self.master_width, self.master_height * 2 + int(abs(self.duration * self.speed))), pygame.SRCALPHA, 32)
            self.tmp_image.blit(self.start_image,
                                self.start_image.get_rect(
                                    top=self.master_height + int(abs(self.duration * self.speed))))
            self.tmp_image.blit(self.end_image, self.end_image.get_rect(top=0))
            self.tmp_image.blit(self.mid_image, self.mid_image.get_rect(top=self.master_height))
            self.states.pop(0)
        self.dis -= (current_sec - self.last_sec) * self.speed
        self.image = self.tmp_image
        vec1 = pygame.Vector2()
        vec1.from_polar((self.pos, -self.line.angle))
        if vec1.length_squared() == 0:
            vec2 = pygame.Vector2()
            vec2.from_polar((self.dis, -self.line.angle - 90))
        else:
            vec2 = vec1.rotate(-90 if self.pos > 0 else 90)
            vec2.scale_to_length(self.dis)
        if self.duration * self.speed > 0:
            offest = pygame.Vector2(self.image.get_rect().midbottom) - self.image.get_rect().center
            offest.rotate_ip(self.line.angle)
            midbottom = vec1 + vec2 + self.line.center
            self.image = pygame.transform.rotate(self.image, self.line.angle)
            self.rect = self.image.get_rect(center=midbottom + offest)
        else:
            self.image = pygame.transform.flip(self.image, False, True)
            offest = pygame.Vector2(self.image.get_rect().midtop) - self.image.get_rect().center
            offest.rotate_ip(self.line.angle)
            midtop = vec1 + vec2 + self.line.center
            self.image = pygame.transform.rotate(self.image, self.line.angle)
            self.rect = self.image.get_rect(center=midtop + offest)
        self.last_sec = current_sec


def NoteSprite(note, line):
    if isinstance(note, Click):
        return BaseNoteSprite(note, line, 'click')
    if isinstance(note, Drag):
        return BaseNoteSprite(note, line, 'drag')
    if isinstance(note, Flick):
        return BaseNoteSprite(note, line, 'flick')
    else:
        return HoldSprite(note, line)


def preview(resolution=(800, 800), fps=60, size=800):
    global _size
    _size = size
    screen = pygame.display.set_mode(resolution)
    group = pygame.sprite.Group()
    for line in data.lines:
        x = LineSprite(line)
        group.add(x)
        for note in line.notes:
            group.add(NoteSprite(note, x))
    clock = pygame.time.Clock()
    pygame.init()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        clock.tick(fps)
        group.update(pygame.time.get_ticks() / 1000)
        screen.fill((0, 0, 0))
        group.draw(screen)
        pygame.display.update()
    pygame.quit()
