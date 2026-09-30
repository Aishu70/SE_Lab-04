import pygame
import random
import math


PLATFORM_COLOR = (100, 80, 50)
CRUMBLE_COLOR = (155, 105, 55)

LAVA_COLOR = (220, 60, 20)


class Platform:

    def __init__(self, x, y, width, height=16, kind="normal"):
        self.rect = pygame.Rect(
            x,
            y,
            width,
            height
        )

        self.kind = kind

        # 0 means not crumbling yet.
        # Starts at 1 second when player lands.
        self.crumble_timer = 0.0


def generate_platforms(width, base_y, count=30):

    platforms = [
        Platform(
            0,
            base_y,
            width,
            20,
            "normal"
        )
    ]

    y = base_y - 110

    for i in range(count):

        w = random.randint(
            80,
            200
        )

        x = random.randint(
            0,
            width - w
        )

        # Approximately 20% crumble.
        if random.random() < 0.20:
            kind = "crumble"
        else:
            kind = "normal"

        platforms.append(
            Platform(
                x,
                y,
                w,
                16,
                kind
            )
        )

        y -= random.randint(
            80,
            130
        )

    return platforms


def update_platforms(platforms, dt):

    broken = []

    for platform in platforms:

        if (
            platform.kind == "crumble"
            and platform.crumble_timer > 0
        ):

            platform.crumble_timer -= dt

            if platform.crumble_timer <= 0:
                broken.append(platform)

    for platform in broken:

        if platform in platforms:
            platforms.remove(platform)


def draw_platform(screen, platform, cam_y, frame):

    rect = platform.rect.move(
        0,
        -int(cam_y)
    )

    if platform.kind == "crumble":

        # Shake while countdown is active.
        if platform.crumble_timer > 0:

            shake = int(
                math.sin(frame * 1.5) * 4
            )

            rect.x += shake

        pygame.draw.rect(
            screen,
            CRUMBLE_COLOR,
            rect,
            border_radius=4
        )

        # Show countdown.
        if platform.crumble_timer > 0:

            font = pygame.font.SysFont(
                "monospace",
                14,
                bold=True
            )

            text = font.render(
                f"{max(0, platform.crumble_timer):.1f}",
                True,
                (255, 230, 120)
            )

            screen.blit(
                text,
                (
                    rect.centerx
                    - text.get_width() // 2,
                    rect.top - 18
                )
            )

    else:

        pygame.draw.rect(
            screen,
            PLATFORM_COLOR,
            rect,
            border_radius=4
        )


def draw_lava(
    screen,
    lava_y,
    cam_y,
    width,
    height,
    frame
):

    ly = int(
        lava_y - cam_y
    )

    if ly < height:

        pts = [(0, ly)]

        for x in range(
            0,
            width + 20,
            20
        ):

            pts.append(
                (
                    x,
                    ly
                    + int(
                        math.sin(
                            x * 0.08
                            + frame * 0.1
                        ) * 8
                    )
                )
            )

        pts.append(
            (width, height)
        )

        pts.append(
            (0, height)
        )

        pygame.draw.polygon(
            screen,
            LAVA_COLOR,
            pts
        )

        s = pygame.Surface(
            (width, 30),
            pygame.SRCALPHA
        )

        for i in range(15):

            pygame.draw.line(
                s,
                (
                    255,
                    100,
                    0,
                    max(0, 60 - i * 4)
                ),
                (0, i),
                (width, i),
                1
            )

        screen.blit(
            s,
            (0, ly - 15)
        )