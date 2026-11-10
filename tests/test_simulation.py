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
