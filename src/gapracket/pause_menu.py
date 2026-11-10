import pygame

from gapracket.config import PARAM_SPECS, VISCOSITY_PRESETS, PhysicsConfig, reset_config

FONT_COLOR = (230, 230, 230)
TRACK_COLOR = (80, 80, 90)
HANDLE_COLOR = (240, 200, 90)
PANEL_COLOR = (20, 20, 28, 230)
BUTTON_COLOR = (70, 70, 110)
RESET_BUTTON_COLOR = (130, 60, 60)

SLIDER_SPACING = 44
TRACK_X = 260
TRACK_WIDTH = 300
TOP_MARGIN = 30
LEFT_MARGIN = 20
BUTTON_WIDTH = 70
BUTTON_HEIGHT = 26
RESET_BUTTON_WIDTH = 140
RESET_BUTTON_HEIGHT = 30


class PauseMenu:
    def __init__(self, config: PhysicsConfig) -> None:
        self.config = config
        pygame.font.init()
        self.font = pygame.font.SysFont(None, 22)

        self.sliders: dict[str, pygame.Rect] = {}
        y = TOP_MARGIN
        for name in PARAM_SPECS:
            self.sliders[name] = pygame.Rect(TRACK_X, y, TRACK_WIDTH, 10)
            y += SLIDER_SPACING

        self.preset_buttons: dict[str, pygame.Rect] = {}
        bx = TRACK_X
        by = y + 10
        for preset_name in VISCOSITY_PRESETS:
            self.preset_buttons[preset_name] = pygame.Rect(bx, by, BUTTON_WIDTH, BUTTON_HEIGHT)
            bx += BUTTON_WIDTH + 10

        self.reset_button = pygame.Rect(TRACK_X, by + BUTTON_HEIGHT + 14, RESET_BUTTON_WIDTH, RESET_BUTTON_HEIGHT)

        self._dragging: str | None = None

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self.reset_button.collidepoint(pos):
                reset_config(self.config)
                return
            for preset_name, rect in self.preset_buttons.items():
                if rect.collidepoint(pos):
                    self.config.viscosity = VISCOSITY_PRESETS[preset_name]
                    return
            for name, rect in self.sliders.items():
                if rect.inflate(0, 20).collidepoint(pos):
                    self._dragging = name
                    self._set_value_from_x(name, pos[0])
                    return
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._dragging = None
        elif event.type == pygame.MOUSEMOTION and self._dragging is not None:
            self._set_value_from_x(self._dragging, event.pos[0])

    def _set_value_from_x(self, name: str, x: int) -> None:
        spec = PARAM_SPECS[name]
        track = self.sliders[name]
        fraction = max(0.0, min(1.0, (x - track.x) / track.width))
        raw_value = spec.min + fraction * (spec.max - spec.min)
        steps = round((raw_value - spec.min) / spec.step)
        value = max(spec.min, min(spec.max, spec.min + steps * spec.step))
        setattr(self.config, name, value)

    def draw(self, surface: pygame.Surface) -> None:
        panel = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        panel.fill(PANEL_COLOR)
        surface.blit(panel, (0, 0))

        for name, track in self.sliders.items():
            spec = PARAM_SPECS[name]
            value = getattr(self.config, name)
            label = self.font.render(f"{name}: {value:.2f}", True, FONT_COLOR)
            surface.blit(label, (LEFT_MARGIN, track.y - 4))

            pygame.draw.rect(surface, TRACK_COLOR, track)
            fraction = (value - spec.min) / (spec.max - spec.min) if spec.max > spec.min else 0.0
            handle_x = track.x + int(fraction * track.width)
            pygame.draw.circle(surface, HANDLE_COLOR, (handle_x, track.centery), 8)

        for preset_name, rect in self.preset_buttons.items():
            pygame.draw.rect(surface, BUTTON_COLOR, rect)
            label = self.font.render(preset_name, True, FONT_COLOR)
            surface.blit(label, (rect.x + 6, rect.y + 4))

        pygame.draw.rect(surface, RESET_BUTTON_COLOR, self.reset_button, border_radius=4)
        reset_label = self.font.render("Resetar valores", True, FONT_COLOR)
        label_rect = reset_label.get_rect(center=self.reset_button.center)
        surface.blit(reset_label, label_rect)
