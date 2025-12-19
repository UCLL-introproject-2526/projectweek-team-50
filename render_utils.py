from __future__ import annotations

import pygame

# Cache small alpha ellipse surfaces to avoid reallocating every frame.
_SHADOW_CACHE: dict[tuple[int, int, int], pygame.Surface] = {}


def get_ellipse_shadow_surface(width: int, height: int, alpha: int = 90) -> pygame.Surface:
    """Return a cached semi-transparent ellipse surface."""
    width = max(1, int(width))
    height = max(1, int(height))
    alpha = max(0, min(255, int(alpha)))

    key = (width, height, alpha)
    surf = _SHADOW_CACHE.get(key)
    if surf is not None:
        return surf

    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.ellipse(surf, (0, 0, 0, alpha), surf.get_rect())
    _SHADOW_CACHE[key] = surf
    return surf


def draw_ellipse_shadow(
    surface: pygame.Surface,
    *,
    center: tuple[int, int],
    size: tuple[int, int],
    alpha: int = 90,
    offset: tuple[int, int] = (0, 0),
) -> None:
    """Draw a simple ground shadow (ellipse) under a sprite.

    center: screen-space position where the shadow ellipse is centered.
    size: (width, height) of the ellipse.
    offset: additional screen-space offset applied to the ellipse.
    """
    shadow = get_ellipse_shadow_surface(size[0], size[1], alpha=alpha)
    x = int(center[0] - shadow.get_width() // 2 + offset[0])
    y = int(center[1] - shadow.get_height() // 2 + offset[1])
    surface.blit(shadow, (x, y))
