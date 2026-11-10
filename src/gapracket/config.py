from dataclasses import dataclass


@dataclass
class ParamSpec:
    default: float
    min: float
    max: float
    step: float


@dataclass
class PhysicsConfig:
    elastic_k: float = 15.0
    natural_length: float = 120.0
    damping: float = 2.0
    ball_mass: float = 1.0
    gravity: float = 500.0
    restitution: float = 0.8
    viscosity: float = 0.5
    ball_radius: float = 15.0
    paddle_radius: float = 40.0


PARAM_SPECS: dict[str, ParamSpec] = {
    "elastic_k": ParamSpec(default=15.0, min=0.0, max=100.0, step=0.5),
    "natural_length": ParamSpec(default=120.0, min=20.0, max=400.0, step=5.0),
    "damping": ParamSpec(default=2.0, min=0.0, max=20.0, step=0.5),
    "ball_mass": ParamSpec(default=1.0, min=0.1, max=10.0, step=0.1),
    "gravity": ParamSpec(default=500.0, min=0.0, max=2000.0, step=10.0),
    "restitution": ParamSpec(default=0.8, min=0.0, max=1.0, step=0.05),
    "viscosity": ParamSpec(default=0.5, min=0.0, max=10.0, step=0.1),
    "ball_radius": ParamSpec(default=15.0, min=5.0, max=50.0, step=1.0),
    "paddle_radius": ParamSpec(default=40.0, min=10.0, max=100.0, step=1.0),
}

VISCOSITY_PRESETS: dict[str, float] = {
    "vacuo": 0.0,
    "ar": 0.5,
    "agua": 4.0,
    "mel": 9.0,
}


def reset_config(config: PhysicsConfig) -> None:
    for name, spec in PARAM_SPECS.items():
        setattr(config, name, spec.default)
