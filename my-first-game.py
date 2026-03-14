import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fancy Particle Playground")

clock = pygame.time.Clock()

particles = []

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(1, 6)

        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        self.life = random.randint(40, 80)
        self.size = random.randint(3, 7)

        self.color = (
            random.randint(150,255),
            random.randint(100,255),
            random.randint(150,255)
        )

    def update(self):
        self.x += self.vx
        self.y += self.vy

        self.vy += 0.08
        self.life -= 1

    def draw(self, surf):
        if self.life > 0:
            pygame.draw.circle(
                surf,
                self.color,
                (int(self.x), int(self.y)),
                self.size
            )

    def alive(self):
        return self.life > 0


def draw_background(surface, t):
    for y in range(HEIGHT):
        c = int(40 + 30 * math.sin(y * 0.01 + t))
        color = (10, c, 50 + c//2)
        pygame.draw.line(surface, color, (0, y), (WIDTH, y))


running = True
time = 0

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    mouse = pygame.mouse.get_pos()
    buttons = pygame.mouse.get_pressed()

    if buttons[0]:
        for _ in range(8):
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