import pygame
import random
import sys
import math
import json
import os

# 파이게임 초기화
pygame.init()
# 믹서를 명시적 설정으로 초기화 (샘플레이트·채널·버퍼 고정)
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.init()
print(f"[믹서] 초기화 결과: {pygame.mixer.get_init()}")   # (freq, size, channels)

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
LASER_COLOR = (255, 0, 100); GREEN = (50, 205, 50)

clock = pygame.time.Clock()
font = get_korean_font(30); large_font = get_korean_font(70); score_font = get_korean_font(40)
small_font = get_korean_font(24)
stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 3)] for _ in range(150)]

# ── 사운드/BGM 로드 ───────────────────────────────────────────────────
SHOOT_SOUND = None
_shoot_path = "./assets/sounds/ShootSound.wav"
if os.path.exists(_shoot_path):
    try:
        SHOOT_SOUND = pygame.mixer.Sound(_shoot_path)
        SHOOT_SOUND.set_volume(0.5)
        print(f"[사운드] ShootSound 로드 성공, 길이={SHOOT_SOUND.get_length():.2f}s")
    except Exception as e:
        print(f"[경고] ShootSound 로드 실패: {e}")
else:
    print(f"[경고] 파일 없음: {_shoot_path}")

MAIN_BGM   = "./assets/sounds/MainGameBgm.wav"
INGAME_BGM = "./assets/sounds/InGameBgm.wav"

def play_bgm(path):
    if not os.path.exists(path):
        print(f"[경고] BGM 파일 없음: {path}")
        return
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)
        print(f"[BGM] 재생 시작: {path}")
    except Exception as e:
        print(f"[경고] BGM 로드 실패: {e}")

def stop_bgm():
    pygame.mixer.music.stop()

def play_shoot_sound():
    if SHOOT_SOUND:
        SHOOT_SOUND.play()

# ── 플레이어 애니메이션 로드 ──────────────────────────────────────────
PLAYER_ANIM_PATH = "./assets/images/anim/"

def load_player_frames(size=(60, 60)):
    frames = []
    for i in range(1, 4):
        path = os.path.join(PLAYER_ANIM_PATH, f"Player{i}.png")
        try:
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, size)
            frames.append(img)
        except Exception as e:
            print(f"[경고] 플레이어 이미지 로드 실패: {path} → {e}")
    return frames

PLAYER_ANIM_FRAMES = load_player_frames(size=(60, 60))

# 이미지 생성
def make_enemy_images():
    images = {}
    size = (36, 36)
    for name, color in [("normal", RED), ("aim", (255, 100, 100)), ("shooter", PURPLE), ("reloading", DARK_GRAY)]:
        surf = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.polygon(surf, color, [(size[0]//2, 0), (0, size[1]), (size[0]//2, size[1]-8), (size[0], size[1])])
        if name == "reloading": surf.set_alpha(150)
        images[name] = surf
    return images

ENEMY_IMAGES = make_enemy_images()

# ── 적 이미지 로드 ────────────────────────────────────────────────────
METEO_IMG = None
try:
    _meteo_raw = pygame.image.load("./assets/images/Meteo.png").convert_alpha()
    METEO_IMG = pygame.transform.scale(_meteo_raw, (44, 44))
except Exception as e:
    print(f"[경고] Meteo 이미지 로드 실패: {e}")

AIM_IMG = None
try:
    _aim_raw = pygame.image.load("./assets/images/AimMon.png").convert_alpha()
    AIM_IMG = pygame.transform.scale(_aim_raw, (60, 60))
except Exception as e:
    print(f"[경고] AimMon 이미지 로드 실패: {e}")

SHOOTER_IMG = None
try:
    _shooter_raw = pygame.image.load("./assets/images/ShooterMon.png").convert_alpha()
    SHOOTER_IMG = pygame.transform.scale(_shooter_raw, (60, 60))
except Exception as e:
    print(f"[경고] ShooterMon 이미지 로드 실패: {e}")

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

def draw_stars(surf, stars, speed_scale):
    for s in stars:
        s[1] += s[2] * speed_scale
        if s[1] > HEIGHT: s[0] = random.randint(0, WIDTH); s[1] = 0
        pygame.draw.circle(surf, WHITE, (int(s[0]), int(s[1])), s[2])

# ── 화면 흔들림 효과 ──────────────────────────────────────────────────
def screen_shake(game_surf, duration=0.45, intensity=18):
    total_frames = int(duration * FPS)
    for frame in range(total_frames):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()

        progress = frame / total_frames
        cur_intensity = intensity * (1.0 - progress)
        ox = random.randint(-int(cur_intensity), int(cur_intensity))
        oy = random.randint(-int(cur_intensity), int(cur_intensity))

        shaken = game_surf.copy()
        if progress < 0.3:
            alpha = int(200 * (0.3 - progress) / 0.3)
            flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash.fill((255, 0, 0, alpha))
            shaken.blit(flash, (0, 0))

        screen.fill((0, 0, 0))
        screen.blit(shaken, (ox, oy))
        pygame.display.flip()
        clock.tick(FPS)

def start_screen():
    play_bgm(MAIN_BGM)
    button_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 150, 300, 80)
    while True:
        screen.fill((10, 10, 30)); draw_stars(screen, stars, 1)
        title = large_font.render("STAR FALL", True, RED)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 150))
        sub = font.render("very! very! hard", True, WHITE)
        screen.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 - 50))
        pygame.draw.rect(screen, BLUE, button_rect, border_radius=12)
        text = font.render("START GAME", True, WHITE)
        screen.blit(text, (button_rect.centerx - text.get_width()//2, button_rect.centery - text.get_height()//2))
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN and button_rect.collidepoint(e.pos): return

def game_over_screen(time_score):
    scores = save_scores(time_score)
    restart_button = pygame.Rect(WIDTH//2 - 150, HEIGHT - 150, 300, 70)
    pygame.mouse.set_visible(True)
    play_bgm(MAIN_BGM)
    while True:
        screen.fill((15, 10, 25))
        msg = large_font.render("GAME OVER", True, RED)
        screen.blit(msg, (WIDTH//2 - msg.get_width()//2, 80))
        cur_score_txt = score_font.render(f"Your Score: {time_score:.1f}s", True, CYAN)
        screen.blit(cur_score_txt, (WIDTH//2 - cur_score_txt.get_width()//2, 180))
        board_rect = pygame.Rect(WIDTH//2 - 200, 250, 400, 320)
        pygame.draw.rect(screen, (30, 30, 50), board_rect, border_radius=15)
        leader_title = font.render("TOP 5 LEADERBOARD", True, YELLOW)
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
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN and restart_button.collidepoint(e.pos): return True

def main():
    play_bgm(INGAME_BGM)
    player = pygame.Rect(WIDTH//2, HEIGHT-80, 40, 40)
    enemies, enemy_bullets = [], []
    time_score, slow_gauge, spawn_timer = 0.0, 100.0, 0.0
    game_surf = pygame.Surface((WIDTH, HEIGHT))
    pygame.mouse.set_visible(False)
    clock.tick(FPS)

    anim_index = 0
    anim_timer = 0.0
    ANIM_SPEED_NORMAL = 0.12
    ANIM_SPEED_SLOW   = 0.24
    PLAYER_IMG_OFFSET_Y = 8

    while True:
        is_slow = pygame.mouse.get_pressed()[2] and slow_gauge > 0
        time_delta = 0.25 if is_slow else 1.0
        raw_dt = clock.tick(FPS) / 1000.0
        dt = raw_dt * time_delta

        if is_slow: slow_gauge = max(0, slow_gauge - 1.0)
        elif slow_gauge < 100: slow_gauge += 0.5
        time_score += dt

        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()

        player.center = pygame.mouse.get_pos()
        player.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

        if PLAYER_ANIM_FRAMES:
            anim_timer += raw_dt
            interval = ANIM_SPEED_SLOW if is_slow else ANIM_SPEED_NORMAL
            if anim_timer >= interval:
                anim_timer -= interval
                anim_index = (anim_index + 1) % len(PLAYER_ANIM_FRAMES)

        # 스폰
        spawn_timer += dt
        current_spawn_delay = max(0.4, 1.6 - math.log1p(time_score) * 0.18)
        if spawn_timer > current_spawn_delay:
            spawn_timer = 0
            for _ in range(min(3, 1 + int(time_score // 50))):
                x = random.randint(50, WIDTH - 50)
                rect = pygame.Rect(x, -50, 18, 18)
                etype = random.choice(["normal", "aim", "shooter"])
                px, py = player.center; ex, ey = rect.center
                dx, dy = px-ex, py-ey; dist = math.hypot(dx, dy)
                dir_vec = (dx/dist, dy/dist) if dist != 0 else (0, 1)
                enemies.append({
                    "rect": rect, "type": etype, "cooldown": random.uniform(100, 180),
                    "stop_timer": 0, "aiming": False, "aim_timer": 0,
                    "dash_dir": dir_vec, "ammo": random.randint(2, 4), "is_reloading": False,
                    "rotation": 0.0
                })

        died = False

        for en in enemies[:]:
            if en["type"] == "normal":
                en["rect"].x += en["dash_dir"][0] * 4.5 * time_delta
                en["rect"].y += en["dash_dir"][1] * 4.5 * time_delta
            else:
                if en["stop_timer"] > 0: en["stop_timer"] -= raw_dt * 60
                else: en["rect"].y += 2.5 * time_delta

            if not en["is_reloading"]:
                if en["type"] == "shooter":
                    en["cooldown"] -= raw_dt * 60
                    if en["cooldown"] <= 0:
                        px, py = player.center; ex, ey = en["rect"].center
                        dx, dy = px-ex, py-ey; dist = math.hypot(dx, dy)
                        if dist != 0:
                            enemy_bullets.append({"pos": [ex, ey], "vel": [(dx/dist)*6.0, (dy/dist)*6.0]})
                        play_shoot_sound()
                        en["ammo"] -= 1; en["cooldown"] = 170

                elif en["type"] == "aim":
                    if not en["aiming"]:
                        en["cooldown"] -= raw_dt * 60
                        if en["cooldown"] <= 0:
                            px, py = player.center; ex, ey = en["rect"].center
                            dx, dy = px-ex, py-ey; dist = math.hypot(dx, dy)
                            en.update({"aim_dir": (dx/dist, dy/dist) if dist!=0 else (0,1), "aiming": True, "aim_timer": 65, "stop_timer": 65})
                    else:
                        en["aim_timer"] -= raw_dt * 60
                        if en["aim_timer"] <= 0:
                            enemy_bullets.append({"pos": list(en["rect"].center), "vel": [en["aim_dir"][0]*7.5, en["aim_dir"][1]*7.5]})
                            play_shoot_sound()
                            en["ammo"] -= 1; en["aiming"] = False; en["cooldown"] = 200

                if en["ammo"] <= 0: en["is_reloading"] = True

                if player.colliderect(en["rect"]):
                    died = True
                    break

        if not died:
            for eb in enemy_bullets[:]:
                eb["pos"][0] += eb["vel"][0] * time_delta
                eb["pos"][1] += eb["vel"][1] * time_delta
                if player.collidepoint(eb["pos"]):
                    died = True
                    break

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
                en["rotation"] = (en["rotation"] + 4 * time_delta) % 360
                if METEO_IMG:
                    base_img = METEO_IMG
                    if en["is_reloading"]:
                        base_img = METEO_IMG.copy(); base_img.set_alpha(150)
                    img = pygame.transform.rotate(base_img, -en["rotation"])
                else:
                    angle = math.degrees(math.atan2(-en["dash_dir"][1], en["dash_dir"][0])) - 90
                    img = pygame.transform.rotate(ENEMY_IMAGES[img_key], angle)

            elif etype == "aim":
                if AIM_IMG:
                    base_img = AIM_IMG
                    if en["is_reloading"]:
                        base_img = AIM_IMG.copy(); base_img.set_alpha(150)
                    img = base_img
                else:
                    img = pygame.transform.rotate(ENEMY_IMAGES[img_key], 180)

            elif etype == "shooter":
                if SHOOTER_IMG:
                    base_img = SHOOTER_IMG
                    if en["is_reloading"]:
                        base_img = SHOOTER_IMG.copy(); base_img.set_alpha(150)
                    if not en["is_reloading"] and en["cooldown"] < 30:
                        px, py = player.center; ex, ey = en["rect"].center
                        angle = math.degrees(math.atan2(py-ey, -(px-ex))) - 90
                        img = pygame.transform.rotate(base_img, angle)
                    else:
                        img = base_img
                else:
                    if not en["is_reloading"] and en["cooldown"] < 30:
                        px, py = player.center; ex, ey = en["rect"].center
                        angle = math.degrees(math.atan2(py-ey, -(px-ex))) - 90
                        img = pygame.transform.rotate(ENEMY_IMAGES[etype], angle)
                    else:
                        img = pygame.transform.rotate(ENEMY_IMAGES[img_key], 180)
            else:
                img = pygame.transform.rotate(ENEMY_IMAGES[img_key], 180)

            game_surf.blit(img, img.get_rect(center=en["rect"].center).topleft)

        for eb in enemy_bullets:
            pygame.draw.circle(game_surf, RED, (int(eb["pos"][0]), int(eb["pos"][1])), 7)
            pygame.draw.circle(game_surf, BRIGHT_RED, (int(eb["pos"][0]), int(eb["pos"][1])), 3)

        if PLAYER_ANIM_FRAMES:
            frame = PLAYER_ANIM_FRAMES[anim_index]
            draw_pos = (player.centerx - frame.get_width() // 2,
                        player.centery - frame.get_height() // 2 + PLAYER_IMG_OFFSET_Y)
            game_surf.blit(frame, draw_pos)
        else:
            pygame.draw.polygon(game_surf, CYAN if is_slow else BLUE,
                [(player.centerx, player.top),
                 (player.left, player.bottom),
                 (player.centerx, player.bottom - 8),
                 (player.right, player.bottom)])

        screen.fill((0, 0, 0))
        screen.blit(game_surf, (0, 0))
        pygame.draw.rect(screen, (50, 50, 50), (WIDTH//2 - 100, 40, 200, 12), border_radius=5)
        pygame.draw.rect(screen, CYAN, (WIDTH//2 - 100, 40, slow_gauge * 2, 12), border_radius=5)
        screen.blit(font.render(f"SCORE: {time_score:.1f}s", True, WHITE), (30, 30))
        screen.blit(font.render(f"LEVEL {int(time_score // 15) + 1}", True, YELLOW), (WIDTH - 150, 30))
        pygame.display.flip()

        if died:
            screen_shake(game_surf, duration=0.45, intensity=18)
            if game_over_screen(time_score):
                return main()
            return

if __name__ == "__main__":
    start_screen(); main()

