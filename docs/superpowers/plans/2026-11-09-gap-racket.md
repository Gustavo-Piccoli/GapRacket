# GapRacket Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Pygame toy where a mouse-controlled paddle is connected by an elastic (spring + damping) to a ball that bounces off the paddle and the screen walls, with a pause overlay to tune every physics parameter live.

**Architecture:** Pure, independently-testable physics functions (`physics.py`) operate on plain `pygame.math.Vector2` values and are driven each frame by a thin simulation/game loop (`game.py`) that reads mouse input, calls the physics functions, and draws the scene. All tunable values live in one `PhysicsConfig` dataclass (`config.py`) that both the simulation and the pause-menu sliders (`pause_menu.py`) read and write.

**Tech Stack:** Python 3, Pygame (rendering, input, vector math), pytest (unit tests for `physics.py`/`entities.py`/simulation step).

**Spec:** [docs/superpowers/specs/2026-11-09-gap-racket-design.md](../specs/2026-11-09-gap-racket-design.md)

## Global Constraints

- Pygame puro, sem biblioteca de UI adicional (do próprio overlay de pausa).
- Sem pontuação, vitória ou derrota.
- Sem persistência de configurações entre execuções.
- Uma única bolinha e uma única raquete, sem multiplayer/rede.
- Controles: mouse move a raquete (X e Y livre); `ESC` ou `P` pausa/retoma.
- Testes automatizados (`pytest`) só para as funções puras de física/entidades/passo de simulação; a janela gráfica é verificada manualmente.

## Review Focus

- Raquete parada por 1 frame (mouse não se moveu, `dt` pode ser 0 em frames raros) não deve causar `ZeroDivisionError` ao calcular a velocidade da raquete.
- Bolinha exatamente sobre a raquete (distância 0) não deve causar erro ao normalizar o vetor direção na força elástica nem na colisão.
- Coeficiente de restituição em 0 (colisão perfeitamente inelástica) não deve gerar velocidades `NaN`/divergentes — bolinha e raquete devem terminar com velocidade relativa normal igual a zero, não continuar se penetrando.
- Bolinha simultaneamente dentro da raquete e fora dos limites da tela num mesmo frame não deve deixar a posição fora da tela após a correção de colisão (a colisão com a parede deve prevalecer na borda).
- Preset de viscosidade do meio (vácuo/ar/água/mel) deve sempre cair dentro de `min`/`max` definidos em `PARAM_SPECS["viscosity"]`, mesmo que alguém edite os presets depois.

---

## Task 1: Config module

**Files:**
- Create: `src/gapracket/__init__.py` (vazio)
- Create: `src/gapracket/config.py`
- Test: `tests/test_config.py`

**Interfaces:**
- Produces: `ParamSpec` (dataclass: `default: float`, `min: float`, `max: float`, `step: float`); `PhysicsConfig` (dataclass with fields `elastic_k`, `natural_length`, `damping`, `ball_mass`, `gravity`, `restitution`, `viscosity`, `ball_radius`, `paddle_radius`, each `float`, defaulting to the value in `PARAM_SPECS`); `PARAM_SPECS: dict[str, ParamSpec]` keyed by those same field names; `VISCOSITY_PRESETS: dict[str, float]` with keys `"vacuo"`, `"ar"`, `"agua"`, `"mel"`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_config.py
from gapracket.config import PhysicsConfig, PARAM_SPECS, VISCOSITY_PRESETS

def test_param_specs_cover_all_config_fields():
    assert set(PARAM_SPECS.keys()) == set(PhysicsConfig().__dataclass_fields__.keys())

def test_defaults_match_param_specs_and_are_within_bounds():
    config = PhysicsConfig()
    for name, spec in PARAM_SPECS.items():
        value = getattr(config, name)
        assert value == spec.default
        assert spec.min <= value <= spec.max

def test_viscosity_presets_within_bounds():
    spec = PARAM_SPECS["viscosity"]
    for value in VISCOSITY_PRESETS.values():
        assert spec.min <= value <= spec.max
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_config.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'gapracket'`

- [ ] **Step 3: Implement `PhysicsConfig`, `ParamSpec`, `PARAM_SPECS`, `VISCOSITY_PRESETS` in `src/gapracket/config.py`**

Use these exact default/min/max/step values:

| campo | default | min | max | step |
|---|---|---|---|---|
| elastic_k | 15.0 | 0.0 | 100.0 | 0.5 |
| natural_length | 120.0 | 20.0 | 400.0 | 5.0 |
| damping | 2.0 | 0.0 | 20.0 | 0.5 |
| ball_mass | 1.0 | 0.1 | 10.0 | 0.1 |
| gravity | 500.0 | 0.0 | 2000.0 | 10.0 |
| restitution | 0.8 | 0.0 | 1.0 | 0.05 |
| viscosity | 0.5 | 0.0 | 10.0 | 0.1 |
| ball_radius | 15.0 | 5.0 | 50.0 | 1.0 |
| paddle_radius | 40.0 | 10.0 | 100.0 | 1.0 |

`VISCOSITY_PRESETS = {"vacuo": 0.0, "ar": 0.5, "agua": 4.0, "mel": 9.0}`

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_config.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add src/gapracket/__init__.py src/gapracket/config.py tests/test_config.py
git commit -m "feat: add PhysicsConfig and parameter specs"
```

---

## Task 2: Physics forces and integration

**Files:**
- Create: `src/gapracket/physics.py`
- Create: `tests/test_physics.py`

**Interfaces:**
- Consumes: nothing from other tasks (uses only `pygame.math.Vector2`).
- Produces:
  - `elastic_force(ball_pos: Vector2, ball_vel: Vector2, paddle_pos: Vector2, paddle_vel: Vector2, k: float, natural_length: float, damping: float) -> Vector2`
  - `gravity_force(mass: float, gravity: float) -> Vector2`
  - `drag_force(velocity: Vector2, viscosity: float) -> Vector2`
  - `integrate(position: Vector2, velocity: Vector2, force: Vector2, mass: float, dt: float) -> tuple[Vector2, Vector2]`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_physics.py
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_physics.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'gapracket.physics'`

- [ ] **Step 3: Implement `elastic_force`, `gravity_force`, `drag_force`, `integrate` in `src/gapracket/physics.py`**

- `elastic_force`: delta = paddle_pos - ball_pos; if `delta.length() == 0` return `Vector2(0, 0)`; otherwise direction = delta normalized, spring = k * (delta.length() - natural_length), relative_vel = ball_vel - paddle_vel, damp = damping * relative_vel.dot(direction), return `direction * (spring - damp)`.
- `gravity_force`: return `Vector2(0, mass * gravity)`.
- `drag_force`: return `-viscosity * velocity`.
- `integrate`: semi-implicit Euler — `new_velocity = velocity + (force / mass) * dt`, `new_position = position + new_velocity * dt`, return `(new_position, new_velocity)`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_physics.py -v`
Expected: PASS (8 passed)

- [ ] **Step 5: Commit**

```bash
git add src/gapracket/physics.py tests/test_physics.py
git commit -m "feat: add elastic, gravity, drag forces and integrator"
```

---

## Task 3: Collision functions

**Files:**
- Modify: `src/gapracket/physics.py` (append functions)
- Modify: `tests/test_physics.py` (append tests)

**Interfaces:**
- Consumes: nothing new.
- Produces:
  - `reflect_velocity(velocity: Vector2, normal: Vector2, restitution: float) -> Vector2`
  - `resolve_wall_collision(position: Vector2, velocity: Vector2, radius: float, width: float, height: float, restitution: float) -> tuple[Vector2, Vector2]`
  - `resolve_paddle_collision(ball_pos: Vector2, ball_vel: Vector2, ball_radius: float, paddle_pos: Vector2, paddle_vel: Vector2, paddle_radius: float, restitution: float) -> tuple[Vector2, Vector2] | None` — returns `None` when the ball and paddle are not overlapping or are already separating (no collision to resolve).

- [ ] **Step 1: Write the failing tests**

```python
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
        paddle_pos=pygame.math.Vector2(15, 0), paddle_vel=pygame.math.Vector2(0, 0), paddle_radius=10.0,
        restitution=1.0,
    )
    assert result is not None
    new_pos, new_vel = result
    assert new_pos == pygame.math.Vector2(-5.0, 0.0)
    assert new_vel == pygame.math.Vector2(-5.0, 0.0)

def test_resolve_paddle_collision_no_overlap_returns_none():
    result = resolve_paddle_collision(
        ball_pos=pygame.math.Vector2(0, 0), ball_vel=pygame.math.Vector2(0, 0), ball_radius=10.0,
        paddle_pos=pygame.math.Vector2(100, 0), paddle_vel=pygame.math.Vector2(0, 0), paddle_radius=10.0,
        restitution=1.0,
    )
    assert result is None

def test_resolve_paddle_collision_zero_restitution_kills_closing_speed():
    _, new_vel = resolve_paddle_collision(
        ball_pos=pygame.math.Vector2(0, 0), ball_vel=pygame.math.Vector2(5, 0), ball_radius=10.0,
        paddle_pos=pygame.math.Vector2(15, 0), paddle_vel=pygame.math.Vector2(0, 0), paddle_radius=10.0,
        restitution=0.0,
    )
    assert new_vel == pygame.math.Vector2(0.0, 0.0)

def test_resolve_paddle_collision_transfers_paddle_velocity():
    _, new_vel = resolve_paddle_collision(
        ball_pos=pygame.math.Vector2(0, 0), ball_vel=pygame.math.Vector2(0, 0), ball_radius=10.0,
        paddle_pos=pygame.math.Vector2(15, 0), paddle_vel=pygame.math.Vector2(20, 0), paddle_radius=10.0,
        restitution=1.0,
    )
    assert new_vel == pygame.math.Vector2(40.0, 0.0)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_physics.py -v`
Expected: FAIL with `ImportError` / `AttributeError` for the three new functions

- [ ] **Step 3: Implement `reflect_velocity`, `resolve_wall_collision`, `resolve_paddle_collision` in `src/gapracket/physics.py`**

- `reflect_velocity`: `vn = velocity.dot(normal)`; if `vn >= 0` return `velocity` unchanged (already separating); otherwise return `velocity - (1 + restitution) * vn * normal`.
- `resolve_wall_collision`: start from `position`/`velocity`; for each of the 4 walls (`x < radius`, `x > width - radius`, `y < radius`, `y > height - radius`) clamp the offending coordinate to the boundary and call `reflect_velocity` with the wall's inward normal (`Vector2(1,0)`, `Vector2(-1,0)`, `Vector2(0,1)`, `Vector2(0,-1)` respectively); return the final `(position, velocity)` — apply corrections sequentially so a corner hitting two walls in one frame resolves both.
- `resolve_paddle_collision`: `delta = ball_pos - paddle_pos`; `distance = delta.length()`; `min_distance = ball_radius + paddle_radius`; if `distance == 0 or distance >= min_distance` return `None`; `normal = delta / distance`; `relative_vel = ball_vel - paddle_vel`; if `relative_vel.dot(normal) >= 0` return `None`; `new_relative_vel = reflect_velocity(relative_vel, normal, restitution)`; return `(paddle_pos + normal * min_distance, new_relative_vel + paddle_vel)`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_physics.py -v`
Expected: PASS (17 passed)

- [ ] **Step 5: Commit**

```bash
git add src/gapracket/physics.py tests/test_physics.py
git commit -m "feat: add wall and paddle collision resolution"
```

---

## Task 4: Entities (Ball, Paddle)

**Files:**
- Create: `src/gapracket/entities.py`
- Create: `tests/test_entities.py`

**Interfaces:**
- Consumes: nothing (plain dataclasses over `pygame.math.Vector2`).
- Produces:
  - `Ball` (dataclass: `position: Vector2`, `velocity: Vector2`, `radius: float`, `mass: float`)
  - `Paddle` (dataclass: `position: Vector2`, `velocity: Vector2`, `radius: float`) with method `update_from_mouse(self, mouse_position: Vector2, dt: float) -> None` — mutates `self.position` and `self.velocity` in place.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_entities.py
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_entities.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'gapracket.entities'`

- [ ] **Step 3: Implement `Ball` and `Paddle` in `src/gapracket/entities.py`**

`update_from_mouse`: if `dt > 0`, `self.velocity = (mouse_position - self.position) / dt`; else `self.velocity = Vector2(0, 0)`; then `self.position = Vector2(mouse_position)`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_entities.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add src/gapracket/entities.py tests/test_entities.py
git commit -m "feat: add Ball and Paddle entities"
```

---

## Task 5: Simulation step function

**Files:**
- Create: `src/gapracket/simulation.py`
- Create: `tests/test_simulation.py`

**Interfaces:**
- Consumes: `PhysicsConfig` (Task 1); `elastic_force`, `gravity_force`, `drag_force`, `integrate`, `resolve_wall_collision`, `resolve_paddle_collision` (Tasks 2-3); `Ball`, `Paddle` (Task 4).
- Produces: `step_simulation(ball: Ball, paddle: Paddle, config: PhysicsConfig, dt: float, screen_width: float, screen_height: float) -> None` — mutates `ball.position`/`ball.velocity` in place for one frame (applies elastic + gravity + drag forces, integrates, then resolves paddle collision, then wall collision). Later tasks (game loop) call this once per frame when not paused.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_simulation.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_simulation.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'gapracket.simulation'`

- [ ] **Step 3: Implement `step_simulation` in `src/gapracket/simulation.py`**

Order of operations: sum `elastic_force(...) + gravity_force(config.ball_mass, config.gravity) + drag_force(ball.velocity, config.viscosity)`; call `integrate(ball.position, ball.velocity, total_force, config.ball_mass, dt)` and assign the results back to `ball.position`/`ball.velocity`; then call `resolve_paddle_collision(...)` with `config.ball_radius`/`config.paddle_radius`/`config.restitution` and, if it returns non-`None`, assign the returned `(position, velocity)` to the ball; then call `resolve_wall_collision(ball.position, ball.velocity, config.ball_radius, screen_width, screen_height, config.restitution)` and assign its result to the ball.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_simulation.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add src/gapracket/simulation.py tests/test_simulation.py
git commit -m "feat: add per-frame simulation step"
```

---

## Task 6: Game loop and window

**Files:**
- Create: `src/gapracket/game.py`
- Create: `main.py`

**Interfaces:**
- Consumes: `PhysicsConfig` (Task 1), `step_simulation` (Task 5), `Ball`, `Paddle` (Task 4).
- Produces: `GameLoop` class (constructor `GameLoop(screen_width: int = 800, screen_height: int = 600)`) with method `run(self) -> None` that opens the Pygame window and runs until the user closes it. Exposes `self.config: PhysicsConfig`, `self.ball: Ball`, `self.paddle: Paddle`, `self.paused: bool` for Task 7 (`pause_menu.py`) to read/toggle.

- [ ] **Step 1: Implement `GameLoop` in `src/gapracket/game.py`**

Constructor creates `pygame.display` of the given size, a `PhysicsConfig()`, a `Ball` centered on screen, a `Paddle` at the mouse's current position, and `self.paused = False`. `run()` loops at a fixed clock (`pygame.time.Clock().tick(60)`, `dt = 1/60`) until a `pygame.QUIT` event or the window is closed; each iteration: handle events (on `pygame.KEYDOWN` with `K_ESCAPE` or `K_p`, toggle `self.paused`), update `self.paddle` from `pygame.mouse.get_pos()` every frame (even while paused, so the raquete still follows the mouse), call `step_simulation(self.ball, self.paddle, self.config, dt, screen_width, screen_height)` only when not `self.paused`, clear the screen, draw the elastic as a line between paddle and ball, draw the paddle and ball as circles, flip the display.

- [ ] **Step 2: Implement `main.py`**

```python
from gapracket.game import GameLoop

if __name__ == "__main__":
    GameLoop().run()
```

- [ ] **Step 3: Manual verification**

Run: `python main.py`
Expected: a window opens; moving the mouse moves a circle (raquete); another circle (bolinha) is pulled by a visible line (elástico), stretches/bounces with gravity, and bounces off the 4 screen edges; pressing `ESC` or `P` freezes the simulation (raquete still follows the mouse) and pressing it again resumes; closing the window exits cleanly.

- [ ] **Step 4: Commit**

```bash
git add src/gapracket/game.py main.py
git commit -m "feat: add game loop, window and rendering"
```

---

## Task 7: Pause menu overlay with sliders

**Files:**
- Create: `src/gapracket/pause_menu.py`
- Modify: `src/gapracket/game.py` (wire the overlay into `GameLoop`)

**Interfaces:**
- Consumes: `PhysicsConfig`, `PARAM_SPECS`, `VISCOSITY_PRESETS` (Task 1); `GameLoop.config`/`GameLoop.paused` (Task 6).
- Produces: `PauseMenu` class (constructor `PauseMenu(config: PhysicsConfig)`) with methods `handle_event(self, event: pygame.event.Event) -> None` (updates `self.config` in place when a slider is dragged or a viscosity preset button is clicked) and `draw(self, surface: pygame.Surface) -> None` (draws one labeled slider per `PARAM_SPECS` entry, each showing its current numeric value, plus four preset buttons for `VISCOSITY_PRESETS`).

- [ ] **Step 1: Implement `PauseMenu` in `src/gapracket/pause_menu.py`**

Lay out one horizontal slider per entry of `PARAM_SPECS` (label + track + draggable handle + current value as text), stacked vertically with fixed spacing; track the pixel rect of each slider's track and each preset button in `__init__` so `handle_event` can hit-test `pygame.MOUSEBUTTONDOWN`/`MOUSEMOTION` with the left button held, map the mouse x-position within a track to a value between that parameter's `min` and `max` (snapped to its `step`), and set the matching `PhysicsConfig` field via `setattr`. Preset buttons set `config.viscosity` directly to the preset's value.

- [ ] **Step 2: Wire `PauseMenu` into `GameLoop` (`src/gapracket/game.py`)**

In `GameLoop.__init__`, create `self.pause_menu = PauseMenu(self.config)`. In `run()`'s event loop, when `self.paused`, forward every event to `self.pause_menu.handle_event(event)`. After drawing the scene each frame, if `self.paused`, call `self.pause_menu.draw(screen)` on top.

- [ ] **Step 3: Manual verification**

Run: `python main.py`
Expected: pausing shows a list of labeled sliders with current values and four viscosity preset buttons; dragging a slider changes its displayed value and immediately affects the simulation once resumed (e.g. raising `elastic_k` makes the elástico visibly stiffer); clicking a preset button snaps the viscosity slider to that preset's value; resuming hides the overlay and the simulation continues with the new values.

- [ ] **Step 4: Commit**

```bash
git add src/gapracket/pause_menu.py src/gapracket/game.py
git commit -m "feat: add pause menu overlay with live parameter sliders"
```

---

## Task 8: Packaging and docs

**Files:**
- Create: `requirements.txt`
- Create: `README.md`
- Create: `.gitignore`
- Create: `LICENSE`

**Interfaces:**
- Consumes: nothing (final polish, no code interfaces).
- Produces: nothing consumed by other tasks.

- [ ] **Step 1: Create `requirements.txt`**

```
pygame
pytest
```

- [ ] **Step 2: Create `.gitignore`**

Standard Python ignores: `__pycache__/`, `*.pyc`, `.venv/`, `venv/`, `.pytest_cache/`, `*.egg-info/`.

- [ ] **Step 3: Create `README.md`**

Cover: what the project is (one paragraph, matching the spec's "Objetivo"); how to install (`pip install -r requirements.txt`); how to run (`python main.py`); controls (mouse moves the raquete, `ESC`/`P` pauses); the full list of tunable parameters from the spec's table and what each affects; how to run the tests (`pytest`).

- [ ] **Step 4: Create `LICENSE`**

Standard MIT license text for the current year, holder name taken from the GitHub account that will own the repository.

- [ ] **Step 5: Manual verification**

Run (in a fresh virtualenv): `pip install -r requirements.txt && pytest && python main.py`
Expected: dependencies install, all automated tests pass, and the game window opens and behaves as in Tasks 6-7.

- [ ] **Step 6: Commit**

```bash
git add requirements.txt README.md .gitignore LICENSE
git commit -m "docs: add README, license and packaging files"
```
