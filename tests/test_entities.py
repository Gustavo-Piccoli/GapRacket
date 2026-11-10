import pygame

from gapracket.entities import Ball, Paddle


def test_ball_holds_its_fields():
    ball = Ball(position=pygame.math.Vector2(1, 2), velocity=pygame.math.Vector2(0, 0), radius=15.0, mass=1.0)
    assert ball.position == pygame.math.Vector2(1, 2)
    assert ball.radius == 15.0


def test_paddle_update_from_mouse_sets_position_and_velocity():
    paddle = Paddle(position=pygame.math.Vector2(0, 0), velocity=pygame.math.Vector2(0, 0), radius=40.0)
    paddle.update_from_mouse(pygame.math.Vector2(10, 0), dt=0.5)
    assert paddle.position == pygame.math.Vector2(10, 0)
    assert paddle.velocity == pygame.math.Vector2(20, 0)


def test_paddle_update_from_mouse_zero_dt_sets_zero_velocity():
    paddle = Paddle(position=pygame.math.Vector2(0, 0), velocity=pygame.math.Vector2(5, 5), radius=40.0)
    paddle.update_from_mouse(pygame.math.Vector2(10, 0), dt=0.0)
    assert paddle.position == pygame.math.Vector2(10, 0)
    assert paddle.velocity == pygame.math.Vector2(0, 0)


def test_paddle_starts_with_previous_position_equal_to_position():
    paddle = Paddle(position=pygame.math.Vector2(3, 4), velocity=pygame.math.Vector2(0, 0), radius=40.0)
    assert paddle.previous_position == pygame.math.Vector2(3, 4)


def test_paddle_update_from_mouse_tracks_previous_position():
    paddle = Paddle(position=pygame.math.Vector2(0, 0), velocity=pygame.math.Vector2(0, 0), radius=40.0)
    paddle.update_from_mouse(pygame.math.Vector2(10, 0), dt=0.5)
    assert paddle.previous_position == pygame.math.Vector2(0, 0)
    assert paddle.position == pygame.math.Vector2(10, 0)
