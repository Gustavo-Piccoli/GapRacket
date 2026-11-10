from gapracket.config import PhysicsConfig, PARAM_SPECS, VISCOSITY_PRESETS, reset_config


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


def test_reset_config_restores_every_field_to_its_default():
    config = PhysicsConfig()
    for name, spec in PARAM_SPECS.items():
        setattr(config, name, spec.min)

    reset_config(config)

    for name, spec in PARAM_SPECS.items():
        assert getattr(config, name) == spec.default
