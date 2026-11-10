from gapracket.config import PhysicsConfig
from gapracket.entities import Ball, Paddle
from gapracket.physics import (
    drag_force,
    elastic_force,
    gravity_force,
    integrate,
    resolve_paddle_collision,
    resolve_wall_collision,
)


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

    paddle_collision = resolve_paddle_collision(
        ball.position, ball.velocity, config.ball_radius,
        paddle.position, paddle.velocity, config.paddle_radius,
        config.restitution,
    )
    if paddle_collision is not None:
        ball.position, ball.velocity = paddle_collision

    ball.position, ball.velocity = resolve_wall_collision(
        ball.position, ball.velocity, config.ball_radius,
        screen_width, screen_height, config.restitution,
    )
