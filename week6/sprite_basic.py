import pygame

pygame.init()
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Sprite Basics")
clock = pygame.time.Clock()

# ── ① 이미지 로드 ──────────────────────────────
img = pygame.image.load("./assets/images/player.png").convert_alpha()

# ── ② 크기 조절 ────────────────────────────────
img = pygame.transform.scale(img, (300, 300))

# ── ③ Rect로 위치 지정 ─────────────────────────
rect = img.get_rect()
rect.center = (200, 150)  # 화면 중앙

# ── ④ 회전 ─────────────────────────────────────
img = pygame.transform.rotate(img,0)  # 45도 반시계
rect = img.get_rect(center=rect.center)  # 회전 후 중심 유지

running = True
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    screen.fill((30, 30, 40))
    screen.blit(img, rect)  # ← blit으로 화면에 그리기
    pygame.display.flip()

pygame.quit()
