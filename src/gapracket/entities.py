from dataclasses import dataclass, field

import pygame

Vector2 = pygame.math.Vector2


@dataclass
class Ball:
    position: Vector2
    velocity: Vector2
    radius: float
    mass: float


@dataclass
class Paddle:
    position: Vector2
    velocity: Vector2
    radius: float
    previous_position: Vector2 = field(init=False, default=None)

    def __post_init__(self) -> None:
        self.previous_position = Vector2(self.position)

    def update_from_mouse(self, mouse_position: Vector2, dt: float) -> None:
        self.previous_position = Vector2(self.position)
        if dt > 0:
            self.velocity = (mouse_position - self.position) / dt
        else:
            self.velocity = Vector2(0, 0)
        self.position = Vector2(mouse_position)
