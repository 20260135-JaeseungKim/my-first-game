import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fancy Particle Playground")
#변경
clock = pygame.time.Clock()

particles = []

class Particle:
    def __init__(self, x, y):

        self.x = x
        self.y = y

        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(2, 7)

        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        self.life = random.randint(60, 120)
        self.max_life = self.life

        self.size = random.randint(4, 8)

        self.color = (
            random.randint(150,255),
            random.randint(120,255),
            random.randint(180,255)
        )

    def update(self):

        self.x += self.vx
        self.y += self.vy

        # gravity
        self.vy += 0.05

        # drag
        self.vx *= 0.99
        self.vy *= 0.99

        self.life -= 1

    def draw(self, surf):

        if self.life <= 0:
            return

        alpha = int(255 * (self.life / self.max_life))

        glow_surface = pygame.Surface((50,50), pygame.SRCALPHA)

        for r in range(self.size*2, 0, -2):

            glow_alpha = alpha // (r//2 + 1)

            pygame.draw.circle(
                glow_surface,
                (*self.color, glow_alpha),
                (25,25),
                r
            )

        surf.blit(glow_surface, (self.x-25, self.y-25))

    def alive(self):
        return self.life > 0


def draw_background(surface, t):

    for y in range(HEIGHT):

        # 항상 0~255 범위
        r = int(128 + 127 * math.sin(y*0.01 + t))
        g = int(128 + 127 * math.sin(y*0.02 + t*0.8))
        b = int(128 + 127 * math.sin(y*0.015 + t*1.2))

        pygame.draw.line(surface, (r,g,b), (0,y), (WIDTH,y))


running = True
time = 0

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    mouse = pygame.mouse.get_pos()
    buttons = pygame.mouse.get_pressed()

    if buttons[0]:
        for _ in range(12):
            particles.append(Particle(mouse[0], mouse[1]))

    time += 0.03

    draw_background(screen, time)

    for p in particles:
        p.update()
        p.draw(screen)

    particles = [p for p in particles if p.alive()]

    pygame.display.flip()
    clock.tick(60)

pygame.quit()