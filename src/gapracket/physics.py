import pygame

Vector2 = pygame.math.Vector2


def elastic_force(
    ball_pos: Vector2,
    ball_vel: Vector2,
    paddle_pos: Vector2,
    paddle_vel: Vector2,
    k: float,
    natural_length: float,
    damping: float,
) -> Vector2:
    delta = paddle_pos - ball_pos
    distance = delta.length()
    if distance == 0:
        return Vector2(0, 0)
    direction = delta / distance
    spring = k * (distance - natural_length)
    relative_vel = ball_vel - paddle_vel
    damp = damping * relative_vel.dot(direction)
    return direction * (spring - damp)


def gravity_force(mass: float, gravity: float) -> Vector2:
    return Vector2(0, mass * gravity)


def drag_force(velocity: Vector2, viscosity: float) -> Vector2:
    return -viscosity * velocity


def integrate(
    position: Vector2,
    velocity: Vector2,
    force: Vector2,
    mass: float,
    dt: float,
) -> tuple[Vector2, Vector2]:
    new_velocity = velocity + (force / mass) * dt
    new_position = position + new_velocity * dt
    return new_position, new_velocity
