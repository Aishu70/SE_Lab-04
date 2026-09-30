import pygame

SPEED = 4
JUMP_VELOCITY = -13
SPRING_VELOCITY = -22


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.vel_y = 0
        self.on_ground = False
        self.color = (60, 160, 220)

        # Used for the spring bounce animation
        self.spring_recoil = 0.0

    def update(self, keys, platforms, width, dt):

        # -------------------------
        # Horizontal movement
        # -------------------------
        dx = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -SPEED

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = SPEED

        # -------------------------
        # Normal jump
        # -------------------------
        if (
            keys[pygame.K_SPACE]
            or keys[pygame.K_w]
            or keys[pygame.K_UP]
        ) and self.on_ground:

            self.vel_y = JUMP_VELOCITY
            self.on_ground = False

        # IMPORTANT:
        # Store the player's feet position BEFORE
        # applying this frame's vertical movement.
        previous_bottom = self.rect.bottom

        # -------------------------
        # Gravity
        # -------------------------
        self.vel_y = min(self.vel_y + 0.55, 12)

        # -------------------------
        # Horizontal bounds
        # -------------------------
        self.rect.x = max(
            0,
            min(
                width - self.rect.width,
                self.rect.x + dx
            )
        )

        # -------------------------
        # Vertical movement
        # -------------------------
        self.rect.y += int(self.vel_y)

        self.on_ground = False

        # -------------------------
        # Platform collision
        # -------------------------
        for platform in platforms:

            p = platform.rect

            # ONE-WAY PLATFORM COLLISION
            #
            # The player can pass through the bottom
            # of the platform.
            #
            # The player only lands if:
            # 1. They are moving downward.
            # 2. They overlap the platform.
            # 3. Their feet were already at or just above
            #    the platform top before this frame.
            #
            # This fixes the original bug:
            #
            # self.rect.bottom <= p.bottom + 10
            #
            if (
                self.vel_y > 0
                and self.rect.colliderect(p)
                and previous_bottom <= p.top + 2
            ):

                self.rect.bottom = p.top
                self.vel_y = 0
                self.on_ground = True

                # -------------------------
                # Crumbling platform
                # -------------------------
                if (
                    platform.kind == "crumble"
                    and platform.crumble_timer <= 0
                ):
                    platform.crumble_timer = 1.0

                # -------------------------
                # Spring platform
                # -------------------------
                if platform.kind == "spring":

                    # Double jump strength
                    self.vel_y = SPRING_VELOCITY

                    self.on_ground = False

                    # Start recoil animation
                    self.spring_recoil = 0.22

        # Gradually stop the recoil animation
        self.spring_recoil = max(
            0.0,
            self.spring_recoil - dt
        )

    def draw(self, screen, cam_y):

        dr = self.rect.move(
            0,
            -int(cam_y)
        )

        # -------------------------
        # Spring recoil animation
        # -------------------------
        if self.spring_recoil > 0:

            squash = max(
                2,
                int(
                    self.spring_recoil
                    / 0.22
                    * 8
                )
            )

            dr = pygame.Rect(
                dr.x - squash // 2,
                dr.y + squash,
                dr.width + squash,
                max(
                    16,
                    dr.height - squash
                )
            )

        # Player body
        pygame.draw.rect(
            screen,
            self.color,
            dr,
            border_radius=6
        )

        # Player head
        pygame.draw.circle(
            screen,
            (255, 220, 180),
            (
                dr.centerx,
                dr.top + 8
            ),
            7
        )