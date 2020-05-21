import pygame

pool = pygame.sprite.Group()


class Explode(pygame.sprite.Sprite):
    def __init__(self, center, angle=0):
        super().__init__(pool)
        self.image = pygame.transform.rotate(
            pygame.transform.scale(pygame.image.load('100.png').convert_alpha(), (100, 100)), angle)
        self.rect = self.image.get_rect(center=center)


pygame.init()
screen = pygame.display.set_mode((500, 500))
clock = pygame.time.Clock()

Explode((100, 100), 180)

while True:
    clock.tick(60)
    pool.update()
    pool.draw(screen)
    pygame.display.update()
