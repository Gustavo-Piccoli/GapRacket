import math

import pygame

from gapracket.config import PhysicsConfig
from gapracket.entities import Ball, Paddle
from gapracket.simulation import step_simulation


def test_step_simulation_moves_ball_toward_paddle_when_stretched():
    config = PhysicsConfig(elastic_k=50.0, natural_length=50.0, damping=0.0, gravity=0.0, viscosity=0.0, restitution=1.0)
    ball = Ball(position=pygame.math.Vector2(0, 0), velocity=pygame.math.Vector2(0, 0), radius=10.0, mass=1.0)
    paddle = Paddle(position=pygame.math.Vector2(200, 0), velocity=pygame.math.Vector2(0, 0), radius=10.0)

    step_simulation(ball, paddle, config, dt=0.01, screen_width=800, screen_height=600)

    assert ball.velocity.x > 0
    assert ball.position.x > 0


def test_step_simulation_resolves_wall_collision_after_integration():
    config = PhysicsConfig(elastic_k=0.0, damping=0.0, gravity=0.0, viscosity=0.0, restitution=1.0)
    ball = Ball(position=pygame.math.Vector2(5, 300), velocity=pygame.math.Vector2(-100, 0), radius=5.0, mass=1.0)
    paddle = Paddle(position=pygame.math.Vector2(400, 300), velocity=pygame.math.Vector2(0, 0), radius=10.0)

    step_simulation(ball, paddle, config, dt=0.1, screen_width=800, screen_height=600)

    assert ball.position.x >= 5.0
    assert ball.velocity.x > 0


def test_step_simulation_stays_finite_with_extreme_parameters():
    # Reproduces the review finding: damping/viscosity/mass at their slider
    # extremes must not diverge to inf/NaN over many frames.
    config = PhysicsConfig(
        elastic_k=100.0, natural_length=20.0, damping=20.0, ball_mass=0.1,
        gravity=2000.0, restitution=1.0, viscosity=10.0, ball_radius=5.0, paddle_radius=10.0,
    )
    ball = Ball(position=pygame.math.Vector2(400, 300), velocity=pygame.math.Vector2(0, 0), radius=config.ball_radius, mass=config.ball_mass)
    paddle = Paddle(position=pygame.math.Vector2(400, 300), velocity=pygame.math.Vector2(0, 0), radius=config.paddle_radius)

    for _ in range(600):
        step_simulation(ball, paddle, config, dt=1 / 60, screen_width=800, screen_height=600)
        assert math.isfinite(ball.position.x) and math.isfinite(ball.position.y)
        assert math.isfinite(ball.velocity.x) and math.isfinite(ball.velocity.y)
