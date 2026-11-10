import math

import pygame

from gapracket.config import PhysicsConfig
from gapracket.entities import Ball, Paddle
from gapracket.physics import (
    clamp_speed,
    drag_force,
    elastic_force,
    gravity_force,
    integrate,
    resolve_paddle_collision,
    resolve_wall_collision,
)

# Explicit (semi-implicit Euler) integration of damping/drag can overshoot and
# diverge to inf/NaN at the slider extremes (high damping+viscosity, low mass).
# Clamping speed after every integration step bounds the feedback loop that
# causes the blow-up; the finite check is a last-resort recovery if it still
# happens (e.g. from a future parameter combination).
MAX_BALL_SPEED = 4000.0


def step_simulation(
    ball: Ball,
    paddle: Paddle,
    config: PhysicsConfig,
    dt: float,
    screen_width: float,
    screen_height: float,
) -> None:
    total_force = (
        elastic_force(
            ball.position, ball.velocity, paddle.position, paddle.velocity,
            config.elastic_k, config.natural_length, config.damping,
        )
        + gravity_force(config.ball_mass, config.gravity)
        + drag_force(ball.velocity, config.viscosity)
    )

    ball.position, ball.velocity = integrate(
        ball.position, ball.velocity, total_force, config.ball_mass, dt,
    )

    if not (
        math.isfinite(ball.position.x) and math.isfinite(ball.position.y)
        and math.isfinite(ball.velocity.x) and math.isfinite(ball.velocity.y)
    ):
        ball.position = pygame.math.Vector2(screen_width / 2, screen_height / 2)
        ball.velocity = pygame.math.Vector2(0, 0)
    else:
        ball.velocity = clamp_speed(ball.velocity, MAX_BALL_SPEED)

    paddle_collision = resolve_paddle_collision(
        ball.position, ball.velocity, config.ball_radius,
        paddle.position, paddle.previous_position, paddle.velocity, config.paddle_radius,
        config.restitution,
    )
    if paddle_collision is not None:
        ball.position, ball.velocity = paddle_collision

    ball.position, ball.velocity = resolve_wall_collision(
        ball.position, ball.velocity, config.ball_radius,
        screen_width, screen_height, config.restitution,
    )
