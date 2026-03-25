"""
collision_demo.py
-----------------
Collision detection visualization: Circle / AABB / OBB comparison

Controls:
    Arrow keys : Move player
    C          : Change sprite
    B          : Change bounding box mode (Circle -> AABB -> OBB)
    M          : Change circle radius mode (min / max / diagonal)
    S          : Toggle enemy rotation
    ESC        : Quit

Usage:
    Place in the same folder as sprites.py and run:
    python collision_demo.py
"""

import pygame
import math
from sprites import load_sprite

# ── 상수 ─────────────────────────────────────────────────────────────────────

WIDTH, HEIGHT = 800, 600
FPS           = 60
SPEED         = 4
ROTATE_SPEED  = 1.5

BG_NORMAL    = (50, 50, 60)
BG_HIT       = (200, 180, 0)
COLOR_CIRCLE = (80, 160, 255)
COLOR_AABB   = (255, 80, 80)
COLOR_OBB    = (80, 220, 120)
COLOR_TEXT   = (255, 255, 255)
COLOR_HIT    = (255, 60, 60)

SPRITE_NAMES  = ["rocket", "adventurer", "stone", "sword"]
BB_MODES      = ["circle", "aabb", "obb"]
RADIUS_MODES  = ["min", "max", "diagonal"]

SPRITE_SIZE  = (180, 180)   # 60 x 3배


# ── 유틸 함수 ─────────────────────────────────────────────────────────────────

def fit_surface(surf, max_w, max_h):
    w, h = surf.get_size()
    scale = min(max_w / w, max_h / h)
    return pygame.transform.scale(surf, (int(w * scale), int(h * scale)))



def circle_collide(cx1, cy1, r1, cx2, cy2, r2):
    dx = cx1 - cx2
    dy = cy1 - cy2
    return dx * dx + dy * dy <= (r1 + r2) ** 2


def aabb_collide(rect1, rect2):
    return rect1.colliderect(rect2)


def get_obb_axes(angle_deg, w, h):
    """OBB의 두 분리축 (단위벡터) 반환."""
    a = math.radians(angle_deg)
    ax = (math.cos(a), math.sin(a))
    ay = (-math.sin(a), math.cos(a))
    return ax, ay


def project_obb(cx, cy, w, h, angle_deg, axis):
    """OBB를 axis에 투영한 [min, max] 반환."""
    a = math.radians(angle_deg)
    hw, hh = w / 2, h / 2
    corners = [
        ( hw * math.cos(a) - hh * math.sin(a),  hw * math.sin(a) + hh * math.cos(a)),
        (-hw * math.cos(a) - hh * math.sin(a), -hw * math.sin(a) + hh * math.cos(a)),
        ( hw * math.cos(a) + hh * math.sin(a),  hw * math.sin(a) - hh * math.cos(a)),
        (-hw * math.cos(a) + hh * math.sin(a), -hw * math.sin(a) - hh * math.cos(a)),
    ]
    dots = [cx * axis[0] + cy * axis[1] +
            corner[0] * axis[0] + corner[1] * axis[1]
            for corner in corners]
    return min(dots), max(dots)


def obb_collide(cx1, cy1, w1, h1, a1, cx2, cy2, w2, h2, a2):
    """SAT(분리축 정리)로 OBB 충돌 검사."""
    axes = get_obb_axes(a1, w1, h1) + get_obb_axes(a2, w2, h2)
    for axis in axes:
        mn1, mx1 = project_obb(cx1, cy1, w1, h1, a1, axis)
        mn2, mx2 = project_obb(cx2, cy2, w2, h2, a2, axis)
        if mx1 < mn2 or mx2 < mn1:
            return False
    return True


def draw_obb(surface, color, cx, cy, w, h, angle_deg, thickness=2):
    """OBB를 화면에 그린다."""
    a   = math.radians(angle_deg)
    hw, hh = w / 2, h / 2
    corners = [
        (cx + hw * math.cos(a) - hh * math.sin(a),
         cy + hw * math.sin(a) + hh * math.cos(a)),
        (cx - hw * math.cos(a) - hh * math.sin(a),
         cy - hw * math.sin(a) + hh * math.cos(a)),
        (cx - hw * math.cos(a) + hh * math.sin(a),
         cy - hw * math.sin(a) - hh * math.cos(a)),
        (cx + hw * math.cos(a) + hh * math.sin(a),
         cy + hw * math.sin(a) - hh * math.cos(a)),
    ]
    pygame.draw.polygon(surface, color, corners, thickness)


# ── 게임 오브젝트 ─────────────────────────────────────────────────────────────

class GameObject:
    def __init__(self, x, y, sprite_name):
        self.x       = float(x)
        self.y       = float(y)
        self.angle   = 0.0
        self.set_sprite(sprite_name)

    def set_sprite(self, name):
        self.name     = name
        base          = load_sprite(name)
        self.base_img = fit_surface(base, *SPRITE_SIZE)
        self.image    = self.base_img
        self.angle    = 0.0
        # 투명 여백을 제외한 실제 콘텐츠 영역
        br        = self.base_img.get_bounding_rect()
        self._bw  = br.width
        self._bh  = br.height
        # surface 전체 중심 기준으로 콘텐츠 중심의 offset
        sw, sh    = self.base_img.get_size()
        self._ox  = br.centerx - sw / 2   # 오른쪽이 양수
        self._oy  = br.centery - sh / 2   # 아래가 양수

    @property
    def w(self): return self._bw
    @property
    def h(self): return self._bh

    @property
    def cx(self): return self.x + self._ox
    @property
    def cy(self): return self.y + self._oy

    @property
    def rect(self):
        return pygame.Rect(
            self.cx - self.w / 2,
            self.cy - self.h / 2,
            self.w, self.h
        )

    def radius(self, mode="diagonal"):
        if mode == "min":
            return min(self.w, self.h) / 2
        elif mode == "max":
            return max(self.w, self.h) / 2
        else:  # diagonal
            return math.sqrt(self.w * self.w + self.h * self.h) / 2

    def rotate(self, da):
        self.angle = (self.angle + da) % 360
        self.image = pygame.transform.rotate(self.base_img, -self.angle)

    def draw(self, surface):
        r = self.image.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(self.image, r)

    def draw_bb(self, surface, mode, radius_mode="diagonal"):
        if mode == "circle":
            pygame.draw.circle(surface, COLOR_CIRCLE,
                               (int(self.cx), int(self.cy)),
                               int(self.radius(radius_mode)), 2)
        elif mode == "aabb":
            pygame.draw.rect(surface, COLOR_AABB, self.rect, 2)
        elif mode == "obb":
            draw_obb(surface, COLOR_OBB,
                     self.cx, self.cy, self.w, self.h, self.angle)


# ── 메인 ─────────────────────────────────────────────────────────────────────

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Collision Detection Visualization")
    clock  = pygame.font.SysFont(None, 56)   # 28 x 2
    small  = pygame.font.SysFont(None, 44)   # 22 x 2
    tick   = pygame.time.Clock()

    sprite_idx = 0
    bb_idx     = 0
    radius_idx = 0
    rotating   = False

    player = GameObject(200, HEIGHT // 2, SPRITE_NAMES[sprite_idx])
    enemy  = GameObject(560, HEIGHT // 2, SPRITE_NAMES[sprite_idx])

    running = True
    while running:
        # ── 이벤트 ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_c:
                    sprite_idx = (sprite_idx + 1) % len(SPRITE_NAMES)
                    player.set_sprite(SPRITE_NAMES[sprite_idx])
                    enemy.set_sprite(SPRITE_NAMES[sprite_idx])
                if event.key == pygame.K_b:
                    bb_idx = (bb_idx + 1) % len(BB_MODES)
                if event.key == pygame.K_m:
                    radius_idx = (radius_idx + 1) % len(RADIUS_MODES)
                if event.key == pygame.K_s:
                    rotating = not rotating

        # ── 업데이트 ──
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:  player.x -= SPEED
        if keys[pygame.K_RIGHT]: player.x += SPEED
        if keys[pygame.K_UP]:    player.y -= SPEED
        if keys[pygame.K_DOWN]:  player.y += SPEED

        # 화면 밖으로 나가지 않게
        player.x = max(player.w / 2, min(WIDTH  - player.w / 2, player.x))
        player.y = max(player.h / 2, min(HEIGHT - player.h / 2, player.y))

        if rotating:
            enemy.rotate(ROTATE_SPEED)

        # ── 충돌 판정 ──
        mode        = BB_MODES[bb_idx]
        radius_mode = RADIUS_MODES[radius_idx]
        if mode == "circle":
            hit = circle_collide(player.cx, player.cy, player.radius(radius_mode),
                                 enemy.cx,  enemy.cy,  enemy.radius(radius_mode))
        elif mode == "aabb":
            hit = aabb_collide(player.rect, enemy.rect)
        else:
            hit = obb_collide(player.cx, player.cy, player.w, player.h, player.angle,
                              enemy.cx,  enemy.cy,  enemy.w,  enemy.h,  enemy.angle)

        # ── 그리기 ──
        bg = BG_HIT if hit else BG_NORMAL
        screen.fill(bg)

        player.draw(screen)
        enemy.draw(screen)
        player.draw_bb(screen, mode, radius_mode)
        enemy.draw_bb(screen, mode, radius_mode)

        # HUD
        mode_color   = {"circle": COLOR_CIRCLE, "aabb": COLOR_AABB, "obb": COLOR_OBB}[mode]
        mode_label   = {"circle": "Circle", "aabb": "AABB", "obb": "OBB"}[mode]
        radius_label = {"min": "min(w,h)/2", "max": "max(w,h)/2", "diagonal": "sqrt(w²+h²)/2"}[radius_mode]

        lines = [
            (f"BB: {mode_label}  [B to change]",                       mode_color),
            (f"Sprite: {SPRITE_NAMES[sprite_idx]}  [C to change]",     COLOR_TEXT),
            (f"Rotate: {'ON' if rotating else 'OFF'}  [S to toggle]",  COLOR_TEXT),
        ]
        if mode == "circle":
            lines.append((f"Radius: {radius_label}  [M to change]",   COLOR_CIRCLE))

        for i, (text, color) in enumerate(lines):
            surf = small.render(text, True, color)
            screen.blit(surf, (10, 10 + i * 44))

        if hit:
            hit_surf = clock.render(f"{mode_label}: HIT!", True, COLOR_HIT)
            screen.blit(hit_surf, (WIDTH // 2 - hit_surf.get_width() // 2, 20))

        pygame.display.flip()
        tick.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()