from dataclasses import dataclass

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

    def update_from_mouse(self, mouse_position: Vector2, dt: float) -> None:
        if dt > 0:
            self.velocity = (mouse_position - self.position) / dt
        else:
            self.velocity = Vector2(0, 0)
        self.position = Vector2(mouse_position)
