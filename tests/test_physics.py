import pygame
import pytest

from gapracket.physics import (
    elastic_force,
    gravity_force,
    drag_force,
    integrate,
    reflect_velocity,
    resolve_wall_collision,
    resolve_paddle_collision,
    clamp_speed,
)


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


def test_reflect_velocity_bounces_off_normal():
    result = reflect_velocity(pygame.math.Vector2(0, 5), normal=pygame.math.Vector2(0, -1), restitution=1.0)
    assert result == pygame.math.Vector2(0, -5)


def test_reflect_velocity_restitution_zero_stops_normal_component():
    result = reflect_velocity(pygame.math.Vector2(0, 5), normal=pygame.math.Vector2(0, -1), restitution=0.0)
    assert result == pygame.math.Vector2(0, 0)


def test_reflect_velocity_ignores_separating_motion():
    result = reflect_velocity(pygame.math.Vector2(0, -5), normal=pygame.math.Vector2(0, -1), restitution=1.0)
    assert result == pygame.math.Vector2(0, -5)


def test_resolve_wall_collision_bottom_wall():
    new_pos, new_vel = resolve_wall_collision(
        position=pygame.math.Vector2(50, 195), velocity=pygame.math.Vector2(0, 10),
        radius=10.0, width=400.0, height=200.0, restitution=0.5,
    )
    assert new_pos == pygame.math.Vector2(50, 190)
    assert new_vel == pygame.math.Vector2(0, -5.0)


def test_resolve_wall_collision_no_wall_hit_is_unchanged():
    new_pos, new_vel = resolve_wall_collision(
        position=pygame.math.Vector2(50, 50), velocity=pygame.math.Vector2(1, 1),
        radius=10.0, width=400.0, height=200.0, restitution=0.5,
    )
    assert new_pos == pygame.math.Vector2(50, 50)
    assert new_vel == pygame.math.Vector2(1, 1)


def test_resolve_paddle_collision_overlapping_separates_and_bounces():
    result = resolve_paddle_collision(
        ball_pos=pygame.math.Vector2(0, 0), ball_vel=pygame.math.Vector2(5, 0), ball_radius=10.0,
        paddle_pos=pygame.math.Vector2(15, 0), paddle_prev_pos=pygame.math.Vector2(15, 0),
        paddle_vel=pygame.math.Vector2(0, 0), paddle_radius=10.0,
        restitution=1.0,
    )
    assert result is not None
    new_pos, new_vel = result
    assert new_pos == pygame.math.Vector2(-5.0, 0.0)
    assert new_vel == pygame.math.Vector2(-5.0, 0.0)


def test_resolve_paddle_collision_no_overlap_returns_none():
    result = resolve_paddle_collision(
        ball_pos=pygame.math.Vector2(0, 0), ball_vel=pygame.math.Vector2(0, 0), ball_radius=10.0,
        paddle_pos=pygame.math.Vector2(100, 0), paddle_prev_pos=pygame.math.Vector2(100, 0),
        paddle_vel=pygame.math.Vector2(0, 0), paddle_radius=10.0,
        restitution=1.0,
    )
    assert result is None


def test_resolve_paddle_collision_zero_restitution_kills_closing_speed():
    _, new_vel = resolve_paddle_collision(
        ball_pos=pygame.math.Vector2(0, 0), ball_vel=pygame.math.Vector2(5, 0), ball_radius=10.0,
        paddle_pos=pygame.math.Vector2(15, 0), paddle_prev_pos=pygame.math.Vector2(15, 0),
        paddle_vel=pygame.math.Vector2(0, 0), paddle_radius=10.0,
        restitution=0.0,
    )
    assert new_vel == pygame.math.Vector2(0.0, 0.0)


def test_clamp_speed_limits_magnitude():
    result = clamp_speed(pygame.math.Vector2(3000, 4000), max_speed=1000.0)
    assert result.length() == pytest.approx(1000.0)


def test_clamp_speed_leaves_slow_velocity_unchanged():
    result = clamp_speed(pygame.math.Vector2(1, 2), max_speed=1000.0)
    assert result == pygame.math.Vector2(1, 2)


def test_resolve_paddle_collision_catches_fast_paddle_sweep_through_ball():
    # Reproduces the review finding: a paddle moving fast enough can end the
    # frame far from the ball even though it swept straight through it.
    # paddle_prev_pos/paddle_pos describe that sweep; distance-at-final-
    # position alone (old behavior) would miss it (200 > min_distance 20).
    result = resolve_paddle_collision(
        ball_pos=pygame.math.Vector2(0, 0), ball_vel=pygame.math.Vector2(0, 0), ball_radius=10.0,
        paddle_pos=pygame.math.Vector2(200, 0), paddle_prev_pos=pygame.math.Vector2(-200, 0),
        paddle_vel=pygame.math.Vector2(4000, 0), paddle_radius=10.0,
        restitution=1.0,
    )
    assert result is not None


def test_resolve_paddle_collision_transfers_paddle_velocity():
    # Paddle approaches the stationary ball from the left (paddle_vel points
    # toward the ball), so the collision triggers and transfers momentum.
    _, new_vel = resolve_paddle_collision(
        ball_pos=pygame.math.Vector2(0, 0), ball_vel=pygame.math.Vector2(0, 0), ball_radius=10.0,
        paddle_pos=pygame.math.Vector2(-15, 0), paddle_prev_pos=pygame.math.Vector2(-15, 0),
        paddle_vel=pygame.math.Vector2(20, 0), paddle_radius=10.0,
        restitution=1.0,
    )
    assert new_vel == pygame.math.Vector2(40.0, 0.0)
