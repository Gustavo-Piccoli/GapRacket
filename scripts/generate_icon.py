"""Generates assets/icon.ico from the game's own color palette (ball, elastic,
paddle blade and handle) — no external image needed. Run with Pillow installed:
    python scripts/generate_icon.py
"""
import os

from PIL import Image, ImageDraw

BALL_COLOR = (240, 200, 90, 255)
ELASTIC_COLOR = (150, 150, 170, 255)
PADDLE_COLOR = (90, 180, 240, 255)
HANDLE_COLOR = (120, 80, 50, 255)

ICON_SIZES = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]


def generate_icon(path: str) -> None:
    size = 256
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    draw.line([(200, 86), (132, 150)], fill=ELASTIC_COLOR, width=8)
    draw.rounded_rectangle([110, 190, 150, 236], radius=16, fill=HANDLE_COLOR)
    draw.ellipse([64, 96, 196, 228], fill=PADDLE_COLOR)
    draw.ellipse([168, 24, 228, 84], fill=BALL_COLOR)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    image.save(path, sizes=ICON_SIZES)


if __name__ == "__main__":
    generate_icon(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "icon.ico"))
    print("icon written to assets/icon.ico")
