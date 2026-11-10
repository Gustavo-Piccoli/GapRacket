import pygame

from gapracket.physics import elastic_force, gravity_force, drag_force, integrate


def test_elastic_force_pulls_toward_paddle_when_stretched():
    force = elastic_force(
        ball_pos=pygame.math.Vector2(0, 0),
        ball_vel=pygame.math.Vector2(0, 0),
        paddle_pos=pygame.math.Vector2(200, 0),
        paddle_vel=pygame.math.Vector2(0, 0),
        k=10.0, natural_length=100.0, damping=0.0,
    )
    assert force == pygame.math.Vector2(1000.0, 0.0)


def test_elastic_force_pushes_away_when_compressed():
    force = elastic_force(
        ball_pos=pygame.math.Vector2(0, 0),
        ball_vel=pygame.math.Vector2(0, 0),
        paddle_pos=pygame.math.Vector2(50, 0),
        paddle_vel=pygame.math.Vector2(0, 0),
        k=10.0, natural_length=100.0, damping=0.0,
    )
    assert force == pygame.math.Vector2(-500.0, 0.0)


def test_elastic_force_damps_relative_velocity():
    force = elastic_force(
        ball_pos=pygame.math.Vector2(0, 0),
        ball_vel=pygame.math.Vector2(5, 0),
        paddle_pos=pygame.math.Vector2(100, 0),
        paddle_vel=pygame.math.Vector2(0, 0),
        k=0.0, natural_length=100.0, damping=2.0,
    )
    assert force == pygame.math.Vector2(-10.0, 0.0)


def test_elastic_force_zero_distance_returns_zero_vector():
    force = elastic_force(
        ball_pos=pygame.math.Vector2(10, 10),
        ball_vel=pygame.math.Vector2(0, 0),
        paddle_pos=pygame.math.Vector2(10, 10),
        paddle_vel=pygame.math.Vector2(0, 0),
        k=10.0, natural_length=100.0, damping=1.0,
    )
    assert force == pygame.math.Vector2(0, 0)


def test_gravity_force_scales_with_mass():
    assert gravity_force(mass=2.0, gravity=500.0) == pygame.math.Vector2(0, 1000.0)


def test_drag_force_opposes_velocity():
    assert drag_force(pygame.math.Vector2(4, -2), viscosity=0.5) == pygame.math.Vector2(-2.0, 1.0)


def test_integrate_semi_implicit_euler():
    new_pos, new_vel = integrate(
        position=pygame.math.Vector2(0, 0),
        velocity=pygame.math.Vector2(1, 0),
        force=pygame.math.Vector2(0, 10),
        mass=2.0, dt=0.1,
    )
    assert new_vel == pygame.math.Vector2(1.0, 0.5)
    assert new_pos == pygame.math.Vector2(0.1, 0.05)
