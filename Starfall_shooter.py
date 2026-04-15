import pygame
import random
import sys
import math
import json
import os

# 파이게임 초기화
pygame.init()

def get_korean_font(size):
    candidates = ["malgungothic", "applegothic", "nanumgothic", "notosanscjk"]
    for name in candidates:
        font = pygame.font.SysFont(name, size)
        if font.get_ascent() > 0:
            return font
    return pygame.font.SysFont(None, size)

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
FPS = 60

# 색상 정의
WHITE = (255, 255, 255); GRAY = (20, 20, 40); DARK_GRAY = (60, 60, 60)
BLUE = (50, 150, 255); RED = (255, 50, 50); BRIGHT_RED = (255, 100, 100)
PURPLE = (180, 80, 255); CYAN = (0, 255, 255); YELLOW = (255, 255, 0)
LASER_COLOR = (255, 0, 100)

clock = pygame.time.Clock()
font = get_korean_font(30); large_font = get_korean_font(70); score_font = get_korean_font(40)
stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 3)] for _ in range(150)]

# 리더보드 로직
SCORE_FILE = "highscores.json"
def load_scores():
    if os.path.exists(SCORE_FILE):
        try:
            with open(SCORE_FILE, "r") as f: return sorted(json.load(f), reverse=True)[:5]
        except: return [0.0] * 5
    return [0.0] * 5

def save_scores(new_score):
    scores = load_scores(); scores.append(round(new_score, 1))
    scores = sorted(list(set(scores)), reverse=True)[:5]
    with open(SCORE_FILE, "w") as f: json.dump(scores, f)
    return scores

# 이미지 생성
def make_enemy_images():
    images = {}
    size = (36, 36)
    # 기본 이미지는 삼각형 꼭지점이 위를 향하도록 그립니다.
    for name, color in [("normal", RED), ("aim", (255, 100, 100)), ("shooter", PURPLE), ("reloading", DARK_GRAY)]:
        surf = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.polygon(surf, color, [(size[0]//2, 0), (0, size[1]), (size[0]//2, size[1]-8), (size[0], size[1])])
        if name == "reloading": surf.set_alpha(150) # 재장전 적은 투명하게
        images[name] = surf
    return images

ENEMY_IMAGES = make_enemy_images()

def draw_stars(surf, stars, speed_scale):
    for s in stars:
        s[1] += s[2] * speed_scale
        if s[1] > HEIGHT: s[0] = random.randint(0, WIDTH); s[1] = 0
        pygame.draw.circle(surf, WHITE, (int(s[0]), int(s[1])), s[2])

def start_screen():
    button_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 150, 300, 80)
    while True:
        screen.fill((10, 10, 30)); draw_stars(screen, stars, 1)
        title = large_font.render("INFINITE SWARM", True, RED)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 150))
        sub = font.render("Red drones dash, Purple drones aim!", True, WHITE)
        screen.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 - 50))
        pygame.draw.rect(screen, BLUE, button_rect, border_radius=12)
        text = font.render("START GAME", True, WHITE)
        screen.blit(text, (button_rect.centerx - text.get_width()//2, button_rect.centery - text.get_height()//2))
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN and button_rect.collidepoint(e.pos): return

def game_over_screen(time_score):
    scores = save_scores(time_score); restart_button = pygame.Rect(WIDTH//2 - 150, HEIGHT - 150, 300, 70)
    pygame.mouse.set_visible(True)
    while True:
        screen.fill((15, 10, 25))
        msg = large_font.render("GAME OVER", True, RED)
        screen.blit(msg, (WIDTH//2 - msg.get_width()//2, 80))
        cur_score_txt = score_font.render(f"Your Score: {time_score:.1f}s", True, CYAN)
        screen.blit(cur_score_txt, (WIDTH//2 - cur_score_txt.get_width()//2, 180))
        board_rect = pygame.Rect(WIDTH//2 - 200, 250, 400, 320)
        pygame.draw.rect(screen, (30, 30, 50), board_rect, border_radius=15)
        leader_title = font.render("🏆 TOP 5 LEADERBOARD", True, YELLOW)
        screen.blit(leader_title, (WIDTH//2 - leader_title.get_width()//2, 270))
        for i, s in enumerate(scores):
            color = YELLOW if round(time_score, 1) == s else WHITE
            rank_txt = font.render(f"{i+1}st: {s:.1f}s", True, color)
            screen.blit(rank_txt, (WIDTH//2 - 80, 330 + (i * 45)))
        pygame.draw.rect(screen, BLUE, restart_button, border_radius=10)
        btn_text = font.render("TRY AGAIN", True, WHITE)
        screen.blit(btn_text, (restart_button.centerx - btn_text.get_width()//2, restart_button.centery - btn_text.get_height()//2))
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN and restart_button.collidepoint(e.pos): return True

def main():
    player = pygame.Rect(WIDTH//2, HEIGHT-80, 40, 40)
    enemies, enemy_bullets = [], []
    time_score, slow_gauge, spawn_timer = 0.0, 100.0, 0.0
    game_surf = pygame.Surface((WIDTH, HEIGHT))
    pygame.mouse.set_visible(False)
    clock.tick(FPS)

    while True:
        is_slow = pygame.mouse.get_pressed()[2] and slow_gauge > 0
        time_delta = 0.25 if is_slow else 1.0
        raw_dt = clock.tick(FPS) / 1000.0
        dt = raw_dt * time_delta
        
        if is_slow: slow_gauge = max(0, slow_gauge - 1.8)
        elif slow_gauge < 100: slow_gauge += 0.2
        time_score += dt

        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()

        player.center = pygame.mouse.get_pos()
        player.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

        # 스폰
        spawn_timer += dt
        current_spawn_delay = max(0.15, 1.5 - math.log1p(time_score) * 0.4)
        if spawn_timer > current_spawn_delay:
            spawn_timer = 0
            for _ in range(min(3, 1 + int(time_score // 25))):
                x = random.randint(50, WIDTH - 50)
                rect = pygame.Rect(x, -50, 36, 36)
                etype = random.choice(["normal", "aim", "shooter"])
                # 생성 시 플레이어 방향 계산 (Normal 돌진용)
                px, py = player.center; ex, ey = rect.center
                dx, dy = px-ex, py-ey; dist = math.hypot(dx, dy)
                dir_vec = (dx/dist, dy/dist) if dist != 0 else (0, 1)
                
                enemies.append({
                    "rect": rect, "type": etype, "cooldown": random.uniform(80, 160),
                    "stop_timer": 0, "aiming": False, "aim_timer": 0, 
                    "dash_dir": dir_vec, "ammo": random.randint(2, 4), "is_reloading": False
                })

        # 업데이트
        for en in enemies[:]:
            # 이동
            if en["type"] == "normal":
                # [돌진형] 지정된 방향으로 돌진
                en["rect"].x += en["dash_dir"][0] * 6.5 * time_delta
                en["rect"].y += en["dash_dir"][1] * 6.5 * time_delta
            else:
                # [사격형/저격형] 정지 안했으면 아래로 이동
                if en["stop_timer"] > 0: en["stop_timer"] -= raw_dt * 60
                else: en["rect"].y += 2.8 * time_delta
            
            # 사격 로직 및 충돌 처리
            if not en["is_reloading"]:
                # Shooter: 플레이어를 조준해서 발사
                if en["type"] == "shooter":
                    en["cooldown"] -= raw_dt * 60
                    if en["cooldown"] <= 0:
                        px, py = player.center; ex, ey = en["rect"].center
                        dx, dy = px-ex, py-ey; dist = math.hypot(dx, dy)
                        if dist != 0:
                            enemy_bullets.append({"pos": [ex, ey], "vel": [(dx/dist)*7, (dy/dist)*7]})
                        en["ammo"] -= 1; en["cooldown"] = 140
                
                # Aim: 레이저 조준 후 발사
                elif en["type"] == "aim":
                    if not en["aiming"]:
                        en["cooldown"] -= raw_dt * 60
                        if en["cooldown"] <= 0:
                            px, py = player.center; ex, ey = en["rect"].center
                            dx, dy = px-ex, py-ey; dist = math.hypot(dx, dy)
                            en.update({"aim_dir": (dx/dist, dy/dist) if dist!=0 else (0,1), "aiming": True, "aim_timer": 55, "stop_timer": 55})
                    else:
                        en["aim_timer"] -= raw_dt * 60
                        if en["aim_timer"] <= 0:
                            enemy_bullets.append({"pos": list(en["rect"].center), "vel": [en["aim_dir"][0]*9.5, en["aim_dir"][1]*9.5]})
                            en["ammo"] -= 1; en["aiming"] = False; en["cooldown"] = 180
                
                if en["ammo"] <= 0: en["is_reloading"] = True

                # 충돌 판정 (재장전 적은 제외)
                if player.colliderect(en["rect"]):
                    if game_over_screen(time_score): return main()
                    return

        for eb in enemy_bullets[:]:
            eb["pos"][0] += eb["vel"][0] * time_delta; eb["pos"][1] += eb["vel"][1] * time_delta
            if player.collidepoint(eb["pos"]):
                if game_over_screen(time_score): return main()
                return

        enemies = [en for en in enemies if -100 < en["rect"].y < HEIGHT + 100 and -100 < en["rect"].x < WIDTH + 100]
        enemy_bullets = [eb for eb in enemy_bullets if -50 < eb["pos"][1] < HEIGHT + 50]

        # 그리기
        game_surf.fill(GRAY); draw_stars(game_surf, stars, 1 + (time_score * 0.04))
        for en in enemies:
            if en["type"] == "aim" and en["aiming"] and not en["is_reloading"]:
                dx, dy = en["aim_dir"]; ex, ey = en["rect"].center
                if en["aim_timer"] > 15 or (pygame.time.get_ticks() // 100) % 2 == 0:
                    pygame.draw.line(game_surf, LASER_COLOR, (ex, ey), (ex + dx*2500, ey + dy*2500), 2)
            
            etype = en["type"]
            img_key = "reloading" if en["is_reloading"] else etype
            
            if etype == "normal":
                # [돌진형] dash_dir 방향 바라보게 회전
                angle = math.degrees(math.atan2(-en["dash_dir"][1], en["dash_dir"][0])) - 90
                img = pygame.transform.rotate(ENEMY_IMAGES[img_key], angle)
            elif etype == "shooter" and not en["is_reloading"]:
                # [저격형] 사격 직전/직후에 플레이어 바라보게 회전
                if en["cooldown"] < 30: # 사격 쿨타임 임박 시 조준 시각화
                    px, py = player.center; ex, ey = en["rect"].center
                    angle = math.degrees(math.atan2(-(py-ey), px-ex)) - 90
                    img = pygame.transform.rotate(ENEMY_IMAGES[etype], angle)
                else:
                    img = pygame.transform.rotate(ENEMY_IMAGES[etype], 180) # 기본은 아래
            else:
                img = pygame.transform.rotate(ENEMY_IMAGES[img_key], 180) # 나머지는 아래
                
            game_surf.blit(img, img.get_rect(center=en["rect"].center).topleft)
            
        for eb in enemy_bullets:
            pygame.draw.circle(game_surf, RED, (int(eb["pos"][0]), int(eb["pos"][1])), 7)
            pygame.draw.circle(game_surf, BRIGHT_RED, (int(eb["pos"][0]), int(eb["pos"][1])), 3)
        
        # 플레이어
        pygame.draw.polygon(game_surf, CYAN if is_slow else BLUE, [(player.centerx, player.top), (player.left, player.bottom), (player.centerx, player.bottom - 8), (player.right, player.bottom)])

        screen.fill((0,0,0)); screen.blit(game_surf, (0, 0))
        pygame.draw.rect(screen, (50, 50, 50), (WIDTH//2 - 100, 40, 200, 12), border_radius=5)
        pygame.draw.rect(screen, CYAN, (WIDTH//2 - 100, 40, slow_gauge * 2, 12), border_radius=5)
        screen.blit(font.render(f"SCORE: {time_score:.1f}s", True, WHITE), (30, 30))
        screen.blit(font.render(f"LEVEL {int(time_score // 15) + 1}", True, YELLOW), (WIDTH - 150, 30))
        pygame.display.flip()

if __name__ == "__main__":
    start_screen(); main()