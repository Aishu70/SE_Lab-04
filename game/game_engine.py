import pygame

from game.player import Player

from game.world import (
    generate_platforms,
    update_platforms,
    draw_platform,
    draw_lava
)


WIDTH, HEIGHT = 500, 640
FPS = 60

BG = (20, 15, 30)

GROUND_Y = HEIGHT + 200


# ============================================================
# TASK 4 - LAVA BURST SETTINGS
# ============================================================

# Lava Burst happens every 15 seconds.
BURST_INTERVAL = 15.0

# Lava Burst lasts for 3 seconds.
BURST_DURATION = 3.0

# During the burst, lava moves 2.5 times faster.
BURST_MULTIPLIER = 2.5


class GameEngine:

    def __init__(self):

        pygame.init()

        self.screen = pygame.display.set_mode(
            (WIDTH, HEIGHT)
        )

        pygame.display.set_caption(
            "Lava Escape"
        )

        self.clock = pygame.time.Clock()

        # ----------------------------------------------------
        # Fonts
        # ----------------------------------------------------

        self.font = pygame.font.SysFont(
            "monospace",
            24,
            bold=True
        )

        self.small_font = pygame.font.SysFont(
            "monospace",
            18,
            bold=True
        )

        self.big_font = pygame.font.SysFont(
            "monospace",
            42,
            bold=True
        )

        self.reset()

    # ========================================================
    # RESET GAME
    # ========================================================

    def reset(self):

        # ----------------------------------------------------
        # Generate world
        # ----------------------------------------------------

        self.platforms = generate_platforms(
            WIDTH,
            GROUND_Y
        )

        # ----------------------------------------------------
        # Create player
        # ----------------------------------------------------

        self.player = Player(
            WIDTH // 2 - 16,
            GROUND_Y - 50
        )

        # ----------------------------------------------------
        # Camera
        # ----------------------------------------------------

        self.cam_y = 0

        # ----------------------------------------------------
        # Lava
        # ----------------------------------------------------

        self.lava_y = GROUND_Y + 60

        # Initial lava rise speed
        self.lava_rise = 0.4

        # ----------------------------------------------------
        # Game state
        # ----------------------------------------------------

        self.score = 0

        self.game_over = False
        self.won = False

        # Top platform position
        self.top_y = (
            self.platforms[-1].rect.y
        )

        self.frame = 0

        # ====================================================
        # TASK 4 - LAVA BURST TIMER
        # ====================================================

        # Total time since game started.
        self.elapsed_time = 0.0

        # Whether Lava Burst is currently active.
        self.burst_active = False

        # Remaining time for current burst.
        self.burst_remaining = 0.0

        # First burst occurs after 15 seconds.
        self.next_burst = BURST_INTERVAL

    # ========================================================
    # HANDLE EVENTS
    # ========================================================

    def handle_events(self):

        for event in pygame.event.get():

            # Close window
            if event.type == pygame.QUIT:
                return False

            # Restart game
            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_r
            ):

                self.reset()

        return True

    # ========================================================
    # TASK 4 - UPDATE LAVA
    # ========================================================

    def update_lava(self, dt):

        # ----------------------------------------------------
        # Increase total game time
        # ----------------------------------------------------

        self.elapsed_time += dt

        # ----------------------------------------------------
        # Check whether it is time for Lava Burst
        # ----------------------------------------------------

        if (
            not self.burst_active
            and self.elapsed_time >= self.next_burst
        ):

            # Activate burst
            self.burst_active = True

            # Burst lasts for 3 seconds
            self.burst_remaining = BURST_DURATION

            # Schedule next burst 15 seconds later
            self.next_burst += BURST_INTERVAL

        # ----------------------------------------------------
        # Countdown active burst
        # ----------------------------------------------------

        if self.burst_active:

            self.burst_remaining -= dt

            # Burst finished
            if self.burst_remaining <= 0:

                self.burst_remaining = 0

                self.burst_active = False

        # ----------------------------------------------------
        # Determine current lava speed
        # ----------------------------------------------------

        if self.burst_active:

            # Lava moves much faster during burst.
            lava_speed = (
                self.lava_rise
                * BURST_MULTIPLIER
            )

        else:

            # Normal lava speed.
            lava_speed = self.lava_rise

        # ----------------------------------------------------
        # Move lava upward
        # ----------------------------------------------------

        self.lava_y -= lava_speed

        # ----------------------------------------------------
        # Gradually increase normal lava speed
        # ----------------------------------------------------

        self.lava_rise = min(
            1.2,
            self.lava_rise + 0.0003
        )

    # ========================================================
    # UPDATE GAME
    # ========================================================

    def update(self):

        # Do not update after game over
        # or victory.
        if self.game_over or self.won:
            return

        # ----------------------------------------------------
        # Delta time
        # ----------------------------------------------------

        dt = (
            self.clock.get_time()
            / 1000.0
        )

        if dt <= 0:
            dt = 1 / FPS

        # ----------------------------------------------------
        # Keyboard input
        # ----------------------------------------------------

        keys = pygame.key.get_pressed()

        # ----------------------------------------------------
        # Update player
        # ----------------------------------------------------

        self.player.update(
            keys,
            self.platforms,
            WIDTH
        )

        # ----------------------------------------------------
        # Update crumbling platforms
        # ----------------------------------------------------

        update_platforms(
            self.platforms,
            dt
        )

        # ----------------------------------------------------
        # Camera follows player upward
        # ----------------------------------------------------

        target = (
            self.player.rect.centery
            - HEIGHT // 2
        )

        if target < self.cam_y:

            self.cam_y = target

        # ----------------------------------------------------
        # TASK 4 - Update lava
        # ----------------------------------------------------

        self.update_lava(dt)

        # ----------------------------------------------------
        # Calculate player height
        # ----------------------------------------------------

        self.score = max(
            0,
            (
                GROUND_Y
                - self.player.rect.y
            ) // 10
        )

        self.frame += 1

        # ====================================================
        # LAVA COLLISION
        # ====================================================

        if (
            self.player.rect.bottom
            >= self.lava_y
        ):

            self.game_over = True

        # ====================================================
        # VICTORY
        # ====================================================

        if (
            self.player.rect.top
            <= self.top_y - 20
        ):

            self.won = True

    # ========================================================
    # TASK 4 - DANGER METER HUD
    # ========================================================

    def draw_danger_hud(self):

        # ----------------------------------------------------
        # Convert lava rise speed into percentage.
        #
        # Normal starting speed = 0.4
        # Maximum normal speed = 1.2
        # ----------------------------------------------------

        danger = (
            self.lava_rise - 0.4
        ) / (
            1.2 - 0.4
        )

        # Keep value between 0 and 1.
        danger = max(
            0.0,
            min(
                1.0,
                danger
            )
        )

        # Convert to percentage.
        danger_percent = int(
            danger * 100
        )

        # ----------------------------------------------------
        # Meter position and size
        # ----------------------------------------------------

        x = 8
        y = 45

        meter_width = 180
        meter_height = 18

        # ----------------------------------------------------
        # Meter background
        # ----------------------------------------------------

        pygame.draw.rect(
            self.screen,
            (70, 70, 80),
            (
                x,
                y,
                meter_width,
                meter_height
            ),
            border_radius=5
        )

        # ----------------------------------------------------
        # Filled danger portion
        # ----------------------------------------------------

        fill_width = int(
            meter_width * danger
        )

        if fill_width > 0:

            pygame.draw.rect(
                self.screen,
                (235, 70, 35),
                (
                    x,
                    y,
                    fill_width,
                    meter_height
                ),
                border_radius=5
            )

        # ----------------------------------------------------
        # Danger text
        # ----------------------------------------------------

        label = self.small_font.render(
            f"Danger: {danger_percent}%",
            True,
            (240, 220, 200)
        )

        self.screen.blit(
            label,
            (
                x + meter_width + 10,
                y
            )
        )

        # ====================================================
        # LAVA BURST WARNING
        # ====================================================

        if self.burst_active:

            # ------------------------------------------------
            # Main warning
            # ------------------------------------------------

            warning = self.big_font.render(
                "LAVA BURST!",
                True,
                (255, 100, 40)
            )

            self.screen.blit(
                warning,
                (
                    WIDTH // 2
                    - warning.get_width() // 2,
                    75
                )
            )

            # ------------------------------------------------
            # Remaining burst time
            # ------------------------------------------------

            timer = self.font.render(
                f"{self.burst_remaining:.1f}s",
                True,
                (255, 220, 150)
            )

            self.screen.blit(
                timer,
                (
                    WIDTH // 2
                    - timer.get_width() // 2,
                    120
                )
            )

    # ========================================================
    # DRAW GAME
    # ========================================================

    def draw(self):

        # ----------------------------------------------------
        # Background
        # ----------------------------------------------------

        self.screen.fill(BG)

        # ----------------------------------------------------
        # Draw platforms
        # ----------------------------------------------------

        for platform in self.platforms:

            draw_platform(
                self.screen,
                platform,
                self.cam_y,
                self.frame
            )

        # ----------------------------------------------------
        # Draw player
        # ----------------------------------------------------

        self.player.draw(
            self.screen,
            self.cam_y
        )

        # ----------------------------------------------------
        # Draw lava
        # ----------------------------------------------------

        draw_lava(
            self.screen,
            self.lava_y,
            self.cam_y,
            WIDTH,
            HEIGHT,
            self.frame
        )

        # ----------------------------------------------------
        # Height HUD
        # ----------------------------------------------------

        sc = self.font.render(
            f"Height: {self.score}m  R=Restart",
            True,
            (220, 200, 180)
        )

        self.screen.blit(
            sc,
            (8, 10)
        )

        # ----------------------------------------------------
        # TASK 4 - Danger meter + burst warning
        # ----------------------------------------------------

        self.draw_danger_hud()

        # ====================================================
        # GAME OVER MESSAGE
        # ====================================================

        if self.game_over:

            self._msg(
                "LAVA GOT YOU!",
                (220, 80, 40)
            )

        # ====================================================
        # VICTORY MESSAGE
        # ====================================================

        if self.won:

            self._msg(
                "ESCAPED!",
                (80, 220, 100)
            )

        # ----------------------------------------------------
        # Update display
        # ----------------------------------------------------

        pygame.display.flip()

    # ========================================================
    # GAME OVER / VICTORY MESSAGE
    # ========================================================

    def _msg(
        self,
        text,
        color
    ):

        # Transparent overlay
        ov = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        ov.fill(
            (0, 0, 0, 150)
        )

        self.screen.blit(
            ov,
            (0, 0)
        )

        # Main message
        m = self.big_font.render(
            text,
            True,
            color
        )

        # Restart message
        s = self.font.render(
            "Press R to Play Again",
            True,
            (200, 200, 200)
        )

        self.screen.blit(
            m,
            (
                WIDTH // 2
                - m.get_width() // 2,
                HEIGHT // 2 - 40
            )
        )

        self.screen.blit(
            s,
            (
                WIDTH // 2
                - s.get_width() // 2,
                HEIGHT // 2 + 20
            )
        )

    # ========================================================
    # MAIN GAME LOOP
    # ========================================================

    def run(self):

        running = True

        while running:

            # Handle events
            running = self.handle_events()

            # Update game
            self.update()

            # Draw game
            self.draw()

            # Maintain FPS
            self.clock.tick(FPS)

        pygame.quit()