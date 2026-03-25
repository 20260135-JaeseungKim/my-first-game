"""
sprites.py
----------
실습용 스프라이트 모음 (Base64 내장)
외부 파일 없이 .py 하나만 있으면 동작합니다.

사용법:
    from sprites import load_sprite
    image = load_sprite("rocket")        # 원본 크기
    image = load_sprite("rocket", (60, 160))  # 지정 크기

스프라이트 목록:
    "rocket"      118 x 315  (OBB에 적합 - 세로로 긴 직사각형)
    "adventurer"   80 x 110  (AABB에 적합 - 정렬된 직사각형)
    "stone"        70 x  70  (원형에 적합 - 둥근 형태)
    "sword"        70 x  70  (OBB에 적합 - 뾰족한 형태)
"""

import base64
import io
import pygame


# ── Base64 이미지 데이터 ────────────────────────────────────────────────────

_ROCKET = (
    "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"
    "bmNvZGVyqAZ/7gAAAABJRU5ErkJggg=="
)

_ADVENTURER = (
    "iVBORw0KGgoAAAANSUhEUgAAAFAAAABuCAYAAACwYZRwAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFn"
    "ZVJlYWR5ccllPAAAAyZpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/"
    "IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6"
    "bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuNi1jMTM4IDc5LjE1OTgyNCwgMjAxNi8w"
    "OS8xNC0wMTowOTowMSAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9y"
    "Zy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIg"
    "eG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDov"
    "L25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20v"
    "eGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9w"
    "IENDIDIwMTcgKFdpbmRvd3MpIiB4bXBNTTpJbnN0YW5jZUlEPSJ4bXAuaWlkOkY1OUU0OEIzRDczRTEx"
    "RTZCMzU0RUZFNTE3RTE5QjQ2IiB4bXBNTTpEb2N1bWVudElEPSJ4bXAuZGlkOkY1OUU0OEI0RDczRTEx"
    "RTZCMzU0RUZFNTE3RTE5QjQ2Ij4gPHhtcE1NOkRlcml2ZWRGcm9tIHN0UmVmOmluc3RhbmNlSUQ9Inht"
    "cC5paWQ6RjU5RTQ4QjFENzNFMTFFNkIzNTRFRkU1MTdFMTlCNDYiIHN0UmVmOmRvY3VtZW50SUQ9Inht"
    "cC5kaWQ6RjU5RTQ4QjJENzNFMTFFNkIzNTRFRkU1MTdFMTlCNDYiLz4gPC9yZGY6RGVzY3JpcHRpb24+"
    "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"
)

_STONE = (
    "iVBORw0KGgoAAAANSUhEUgAAAEYAAABGCAYAAABxLuKEAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFn"
    "ZVJlYWR5ccllPAAAAyFpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/"
    "IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6"
    "bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuNS1jMDE0IDc5LjE1MTQ4MSwgMjAxMy8w"
    "My8xMy0xMjowOToxNSAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9y"
    "Zy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIg"
    "eG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDov"
    "L25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20v"
    "eGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9w"
    "IENDIChXaW5kb3dzKSIgeG1wTU06SW5zdGFuY2VJRD0ieG1wLmlpZDo3NUZCNjNFQjczMzQxMUUzQjlD"
    "NUI3NDgxQTNDMkQ3OCIgeG1wTU06RG9jdW1lbnRJRD0ieG1wLmRpZDo3NUZCNjNFQzczMzQxMUUzQjlD"
    "NUI3NDgxQTNDMkQ3OCI+IDx4bXBNTTpEZXJpdmVkRnJvbSBzdFJlZjppbnN0YW5jZUlEPSJ4bXAuaWlk"
    "Ojc1RjNEOEQwNzMzNDExRTNCOUM1Qjc0ODFBM0MyRDc4IiBzdFJlZjpkb2N1bWVudElEPSJ4bXAuZGlk"
    "Ojc1RkI2M0VBNzMzNDExRTNCOUM1Qjc0ODFBM0MyRDc4Ii8+IDwvcmRmOkRlc2NyaXB0aW9uPiA8L3Jk"
    "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"
    "AAAAAElFTkSuQmCC"
)

_SWORD = (
    "iVBORw0KGgoAAAANSUhEUgAAAEYAAABGCAYAAABxLuKEAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFn"
    "ZVJlYWR5ccllPAAAAyFpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/"
    "IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6"
    "bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuNS1jMDE0IDc5LjE1MTQ4MSwgMjAxMy8w"
    "My8xMy0xMjowOToxNSAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9y"
    "Zy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIg"
    "eG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDov"
    "L25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20v"
    "eGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9w"
    "IENDIChXaW5kb3dzKSIgeG1wTU06SW5zdGFuY2VJRD0ieG1wLmlpZDo3NUNEOEIwMTczMzQxMUUzQjlD"
    "NUI3NDgxQTNDMkQ3OCIgeG1wTU06RG9jdW1lbnRJRD0ieG1wLmRpZDo3NUNEOEIwMjczMzQxMUUzQjlD"
    "NUI3NDgxQTNDMkQ3OCI+IDx4bXBNTTpEZXJpdmVkRnJvbSBzdFJlZjppbnN0YW5jZUlEPSJ4bXAuaWlk"
    "Ojc1Q0Q4QUZGNzMzNDExRTNCOUM1Qjc0ODFBM0MyRDc4IiBzdFJlZjpkb2N1bWVudElEPSJ4bXAuZGlk"
    "Ojc1Q0Q4QjAwNzMzNDExRTNCOUM1Qjc0ODFBM0MyRDc4Ii8+IDwvcmRmOkRlc2NyaXB0aW9uPiA8L3Jk"
    "ZjpSREY+IDwveDp4bXBtZXRhPiA8P3hwYWNrZXQgZW5kPSJyIj8+OwGVngAAA0NJREFUeNrsnMFqGkEY"
    "x2fWRXuRCH2A+AaxJVBoD90+QU4VSQt6qDWhFyk99BaPPZTUSyHGHlIKRexDdAsVagll8gbmDQwGWs3u"
    "fJ1tbJqiu+6664zOzoAo7mBmf/6///efZQ0GAKTG5MAKjAKjwKwEGIyxr3nfD3fvW+fn6O7zD1/8zF/0"
    "uvVl+YYohRpgmmEvby3DerRlWES3sVvECBtMX7mv+4+KqpTYOG48XbNAIwxM1vo5QGw1/RvDYXbz5acz"
    "kaUkXDE20qoOlCuQCGV+pZK1WCvmx7tn6xcWJeyl4y3IUcw/YjR778XH01gqZmTZtb9QJk48oR3F0nyd"
    "9sxKqOSqNISMzv72VuzAOO3ZRx3WYwXm20Fl67I9zyST7bx5vBcjxfhXArPYauf19rr0YLqNnb3r7Xkm"
    "QsecE5h7++barp0wZ0Oi59aJ/mvXEwvFxvV9lFTtmiXcuhuUmSWFaV3KUuoeVDa82rMP7XHdR3EDAyiC"
    "1sva9/Grh2vSgBmrxQjNhZXhKJkqSQPmzk7jJEI7J5KVEphRfI7fK3wrA0aL5JsGwm+9vPZGiJrhVYdM"
    "6cAkdZ1EUI/yKeb2k7enzGd6oWyXgnyKuWy38/uMcy3Y64reSoOBED6DOfqLAMXMf3IYJAYTLuhhIi2Y"
    "MEGPV7ATBgbj4CUBnP1FjGJgnvQKRHowOg5eShhAfsVsVg7PAgc9iuRXzHgEUAD0eAY7wWCCeAYmIlYo"
    "BEyQoMc72AkFEyzoxUgxQYIe72AnHIyfoCci2IlXjK+gByR2YPwEPRHBTjgYJ+ixJ09FpEYX8QMzNmDi"
    "Fexm3bkpLRiMsRlNOpYMDAJK3P0Fk9iCGQe9/rRjNohVzMJvHGq320X2N0pux5PWIKch+889M2DbV+8P"
    "UzdNjxI8yufz7xfaNTnAz7KH4XZwpKfdVmOI9J+l+JHFMg4FRmAp9dykPxgMcpZlTb0nT9f1fjqdJh6f"
    "udrm6/Uji3K5/JkdN1z2Umaz2XzgsddSpaQ8RoFRYBQYBUaBUWDUUGCWPPm2Wq0N9lT3uSWoFgqFE97J"
    "V8j/dtA0LUMpNdiJe01zgBnOXFVKMdtdTxuEKcHwO1dKj1HmK9n4LcAAwvdMMLRYaKIAAAAASUVORK5C"
    "YII="
)


_SPRITES = {
    "rocket":     _ROCKET,
    "adventurer": _ADVENTURER,
    "stone":      _STONE,
    "sword":      _SWORD,
}


# ── 공개 함수 ───────────────────────────────────────────────────────────────

def load_sprite(name: str, size: tuple = None) -> pygame.Surface:
    """
    스프라이트를 pygame.Surface로 반환합니다.

    Parameters
    ----------
    name : str
        "rocket" | "adventurer" | "stone" | "sword"
    size : tuple, optional
        (width, height) 지정하면 해당 크기로 스케일

    Returns
    -------
    pygame.Surface  (convert_alpha 적용)
    """
    if name not in _SPRITES:
        raise ValueError(
            f"알 수 없는 스프라이트: '{name}'. "
            f"사용 가능: {list(_SPRITES.keys())}"
        )
    raw = base64.b64decode(_SPRITES[name])
    buf = io.BytesIO(raw)
    surface = pygame.image.load(buf).convert_alpha()
    if size is not None:
        surface = pygame.transform.scale(surface, size)
    return surface


if __name__ == "__main__":
    BOX_W        = 100   # 각 스프라이트가 들어갈 박스 너비
    BOX_H        = 160   # 각 스프라이트가 들어갈 박스 높이
    PADDING      = 30    # 스프라이트 간격
    LABEL_HEIGHT = 24    # 변수명 텍스트 높이

    def fit_surface(surf, box_w, box_h):
        """비율을 유지하면서 박스 안에 맞게 스케일."""
        w, h = surf.get_size()
        scale = min(box_w / w, box_h / h)
        return pygame.transform.scale(surf, (int(w * scale), int(h * scale)))

    names = list(_SPRITES.keys())
    count = len(names)

    win_w = count * (BOX_W + PADDING) + PADDING
    win_h = BOX_H + LABEL_HEIGHT + PADDING * 2

    pygame.init()
    screen = pygame.display.set_mode((win_w, win_h))
    pygame.display.set_caption("sprites.py 미리보기")
    font  = pygame.font.SysFont(None, 22)
    clock = pygame.time.Clock()

    # 원본 비율 유지하면서 로드
    surfaces = {name: fit_surface(load_sprite(name), BOX_W, BOX_H) for name in names}

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        screen.fill((40, 40, 40))

        for i, name in enumerate(names):
            box_x = PADDING + i * (BOX_W + PADDING)
            surf  = surfaces[name]
            sw, sh = surf.get_size()

            # 박스 중앙에 배치
            x = box_x + (BOX_W - sw) // 2
            y = PADDING + (BOX_H - sh) // 2
            screen.blit(surf, (x, y))

            # 변수명 라벨
            label = font.render(f'"{name}"', True, (220, 220, 220))
            lx = box_x + BOX_W // 2 - label.get_width() // 2
            screen.blit(label, (lx, PADDING + BOX_H + 6))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()