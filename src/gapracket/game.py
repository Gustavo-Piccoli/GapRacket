import pygame

from gapracket.config import PhysicsConfig
from gapracket.entities import Ball, Paddle
from gapracket.pause_menu import PauseMenu
from gapracket.simulation import step_simulation

Vector2 = pygame.math.Vector2

BACKGROUND_COLOR = (18, 18, 24)
ELASTIC_COLOR = (90, 90, 110)
PADDLE_COLOR = (90, 180, 240)
HANDLE_COLOR = (120, 80, 50)
BALL_COLOR = (240, 200, 90)
FPS = 60


class GameLoop:
    def __init__(self, screen_width: int = 800, screen_height: int = 600) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height

        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("GapRacket")
        self.clock = pygame.time.Clock()

        self.config = PhysicsConfig()
        self.ball = Ball(
            position=Vector2(screen_width / 2, screen_height / 2),
            velocity=Vector2(0, 0),
            radius=self.config.ball_radius,
            mass=self.config.ball_mass,
        )
        self.paddle = Paddle(
            position=Vector2(pygame.mouse.get_pos()),
            velocity=Vector2(0, 0),
            radius=self.config.paddle_radius,
        )
        self.paused = False
        self.pause_menu = PauseMenu(self.config)

    def run(self) -> None:
        dt = 1 / FPS
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_p):
                    self.paused = not self.paused
                elif self.paused:
                    self.pause_menu.handle_event(event)

            if not self.paused:
                self.paddle.update_from_mouse(Vector2(pygame.mouse.get_pos()), dt)
                step_simulation(
                    self.ball, self.paddle, self.config, dt,
                    self.screen_width, self.screen_height,
                )

            self._draw()
            self.clock.tick(FPS)

        pygame.quit()

    def _draw(self) -> None:
        self.screen.fill(BACKGROUND_COLOR)
        pygame.draw.line(self.screen, ELASTIC_COLOR, self.paddle.position, self.ball.position, 2)
        self._draw_paddle()
        pygame.draw.circle(self.screen, BALL_COLOR, self.ball.position, self.config.ball_radius)
        if self.paused:
            self.pause_menu.draw(self.screen)
        pygame.display.flip()

    def _draw_paddle(self) -> None:
        # Ping-pong paddle look: a round blade (same hitbox as before) with a
        # handle in a fixed orientation (always pointing down), not rotating
        # to face the ball — the simpler of the two options for this toy.
        radius = self.config.paddle_radius
        center = self.paddle.position

        handle_width = radius * 0.45
        handle_height = radius * 0.9
        handle_rect = pygame.Rect(0, 0, handle_width, handle_height)
        handle_rect.midtop = (center.x, center.y + radius - 2)
        pygame.draw.rect(self.screen, HANDLE_COLOR, handle_rect, border_radius=int(handle_width / 2))

        pygame.draw.circle(self.screen, PADDLE_COLOR, center, radius)
