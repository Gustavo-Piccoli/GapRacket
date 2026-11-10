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


def reflect_velocity(velocity: Vector2, normal: Vector2, restitution: float) -> Vector2:
    normal_velocity = velocity.dot(normal)
    if normal_velocity >= 0:
        return velocity
    return velocity - (1 + restitution) * normal_velocity * normal


def resolve_wall_collision(
    position: Vector2,
    velocity: Vector2,
    radius: float,
    width: float,
    height: float,
    restitution: float,
) -> tuple[Vector2, Vector2]:
    new_position = Vector2(position)
    new_velocity = Vector2(velocity)

    if new_position.x < radius:
        new_position.x = radius
        new_velocity = reflect_velocity(new_velocity, Vector2(1, 0), restitution)
    elif new_position.x > width - radius:
        new_position.x = width - radius
        new_velocity = reflect_velocity(new_velocity, Vector2(-1, 0), restitution)

    if new_position.y < radius:
        new_position.y = radius
        new_velocity = reflect_velocity(new_velocity, Vector2(0, 1), restitution)
    elif new_position.y > height - radius:
        new_position.y = height - radius
        new_velocity = reflect_velocity(new_velocity, Vector2(0, -1), restitution)

    return new_position, new_velocity


def _closest_point_on_segment(point: Vector2, segment_start: Vector2, segment_end: Vector2) -> Vector2:
    segment = segment_end - segment_start
    segment_length_squared = segment.length_squared()
    if segment_length_squared == 0:
        return Vector2(segment_start)
    t = (point - segment_start).dot(segment) / segment_length_squared
    t = max(0.0, min(1.0, t))
    return segment_start + segment * t


def resolve_paddle_collision(
    ball_pos: Vector2,
    ball_vel: Vector2,
    ball_radius: float,
    paddle_pos: Vector2,
    paddle_prev_pos: Vector2,
    paddle_vel: Vector2,
    paddle_radius: float,
    restitution: float,
) -> tuple[Vector2, Vector2] | None:
    # Use the closest point on the paddle's path this frame (prev→current),
    # not just its final position, so a fast sweep can't tunnel through the
    # ball between frames.
    contact_point = _closest_point_on_segment(ball_pos, paddle_prev_pos, paddle_pos)

    delta = ball_pos - contact_point
    distance = delta.length()
    min_distance = ball_radius + paddle_radius

    if distance == 0:
        # Dead-center hit: delta can't give a normal, so fall back to the
        # paddle's direction of travel (a stationary paddle exactly
        # concentric with the ball is the genuinely degenerate case).
        travel = paddle_pos - paddle_prev_pos
        if travel.length_squared() == 0:
            return None
        normal = travel.normalize()
    elif distance >= min_distance:
        return None
    else:
        normal = delta / distance

    relative_vel = ball_vel - paddle_vel
    if relative_vel.dot(normal) >= 0:
        return None

    new_relative_vel = reflect_velocity(relative_vel, normal, restitution)
    new_position = contact_point + normal * min_distance
    new_velocity = new_relative_vel + paddle_vel
    return new_position, new_velocity


def clamp_speed(velocity: Vector2, max_speed: float) -> Vector2:
    speed = velocity.length()
    if speed > max_speed:
        return velocity * (max_speed / speed)
    return velocity
