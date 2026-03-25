import pygame
import sys
import math

# Pygame 초기화
pygame.init()

# 창 생성
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("충돌 비교 (Circle / AABB / OBB)")

# FPS
clock = pygame.time.Clock()
FPS = 60

# 폰트
font = pygame.font.SysFont(None, 30)

# 색상
WHITE = (255, 255, 255)
RED_BG = (255, 0, 0)
GRAY = (150, 150, 150)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# 오브젝트
rect1 = pygame.Rect(100, 200, 150, 100)
rect2 = pygame.Rect(0, 0, 200, 150)
rect2.center = (400, 300)

rect2_surf = pygame.Surface((200, 150), pygame.SRCALPHA)
rect2_surf.fill(GRAY)

angle = 0
speed = 5

# ------------------------
# OBB 계산
# ------------------------
def get_obb_points(center, w, h, angle):
    cx, cy = center
    rad = math.radians(angle)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)

    hw, hh = w/2, h/2
    pts = [(-hw,-hh),(hw,-hh),(hw,hh),(-hw,hh)]

    result = []
    for x,y in pts:
        rx = x*cos_a - y*sin_a
        ry = x*sin_a + y*cos_a
        result.append((cx+rx, cy+ry))
    return result

def get_aabb_points(rect):
    return [rect.topleft, rect.topright, rect.bottomright, rect.bottomleft]

# ------------------------
# SAT
# ------------------------
def normalize(v):
    l = math.hypot(v[0], v[1])
    return (v[0]/l, v[1]/l)

def project(points, axis):
    dots = [p[0]*axis[0] + p[1]*axis[1] for p in points]
    return min(dots), max(dots)

def sat_collision(obb1, obb2):
    axes = []
    for obb in [obb1, obb2]:
        for i in range(4):
            p1 = obb[i]
            p2 = obb[(i+1)%4]
            edge = (p2[0]-p1[0], p2[1]-p1[1])
            axis = normalize((-edge[1], edge[0]))
            axes.append(axis)

    for axis in axes:
        min1,max1 = project(obb1, axis)
        min2,max2 = project(obb2, axis)
        if max1 < min2 or max2 < min1:
            return False
    return True

# ------------------------
# 메인 루프
# ------------------------
running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 이동
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]: rect1.x -= speed
    if keys[pygame.K_RIGHT]: rect1.x += speed
    if keys[pygame.K_UP]: rect1.y -= speed
    if keys[pygame.K_DOWN]: rect1.y += speed

    # 회전
    angle += 5 if keys[pygame.K_z] else 1

    # 회전 이미지
    rotated_surf = pygame.transform.rotate(rect2_surf, angle)
    rotated_rect = rotated_surf.get_rect(center=rect2.center)

    # 중심 / 반지름
    c1 = rect1.center
    c2 = rotated_rect.center
    r1 = rect1.width // 2
    r2 = rect2.width // 2

    # 🔵 Circle 충돌
    dx = c1[0] - c2[0]
    dy = c1[1] - c2[1]
    dist = math.sqrt(dx*dx + dy*dy)
    circle_hit = dist <= (r1 + r2)

    # 🔴 AABB 충돌
    aabb_hit = rect1.colliderect(rect2)

    # 🟢 OBB 충돌 (SAT)
    obb1 = get_aabb_points(rect1)

    # 🔥 핵심 수정: -angle
    obb2 = get_obb_points(rotated_rect.center, rect2.width, rect2.height, -angle)

    obb_hit = sat_collision(obb1, obb2)

    # 배경
    screen.fill(RED_BG if obb_hit else WHITE)

    # 그리기
    pygame.draw.rect(screen, GRAY, rect1)
    screen.blit(rotated_surf, rotated_rect)

    pygame.draw.rect(screen, RED, rect1, 2)
    pygame.draw.rect(screen, RED, rect2, 2)

    pygame.draw.circle(screen, BLUE, c1, r1, 2)
    pygame.draw.circle(screen, BLUE, c2, r2, 2)

    pygame.draw.circle(screen, BLUE, c1, 5)
    pygame.draw.circle(screen, BLUE, c2, 5)

    pygame.draw.polygon(screen, GREEN, obb1, 2)
    pygame.draw.polygon(screen, GREEN, obb2, 2)

    # 텍스트
    text1 = font.render(f"Circle: {'HIT' if circle_hit else 'NO'}", True, BLACK)
    text2 = font.render(f"AABB: {'HIT' if aabb_hit else 'NO'}", True, BLACK)
    text3 = font.render(f"OBB: {'HIT' if obb_hit else 'NO'}", True, BLACK)

    screen.blit(text1, (10, 10))
    screen.blit(text2, (10, 40))
    screen.blit(text3, (10, 70))

    pygame.display.flip()

pygame.quit()
sys.exit()