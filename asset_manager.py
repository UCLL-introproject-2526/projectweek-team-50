import os
import re
import math
from dataclasses import dataclass

import pygame


_TOWER_ROOT = os.path.abspath(
	os.path.join(os.path.dirname(__file__), "assets", "TOWER CLASSES FINAL")
)


def _natural_key(name: str):
	return [int(x) if x.isdigit() else x.lower() for x in re.split(r"(\d+)", name)]


def _split_strip(sheet: pygame.Surface) -> list[pygame.Surface]:
	"""Split a horizontal strip into square frames (frame = height x height)."""
	frames: list[pygame.Surface] = []
	w, h = sheet.get_width(), sheet.get_height()
	if h <= 0 or w <= h:
		return frames
	if w % h != 0:
		return frames
	count = w // h
	for i in range(count):
		frame = sheet.subsurface(pygame.Rect(i * h, 0, h, h)).copy()
		frames.append(frame)
	return frames


def _split_horizontal_equal(sheet: pygame.Surface, parts: int) -> list[pygame.Surface]:
	"""Split a sheet into N equal-width frames (full height).

	Used for asset packs where frames aren't square (e.g. goblin 288x80 => 3x 96x80).
	"""
	if parts <= 0:
		return []
	w, h = sheet.get_width(), sheet.get_height()
	if w <= 0 or h <= 0 or w % parts != 0:
		return []
	fw = w // parts
	frames: list[pygame.Surface] = []
	for i in range(parts):
		frame = sheet.subsurface(pygame.Rect(i * fw, 0, fw, h)).copy()
		frames.append(frame)
	return frames


def _split_vertical_strip(sheet: pygame.Surface) -> list[pygame.Surface]:
	"""Split a vertical strip into square frames (frame = width x width)."""
	frames: list[pygame.Surface] = []
	w, h = sheet.get_width(), sheet.get_height()
	if w <= 0 or h <= w:
		return frames
	if h % w != 0:
		return frames
	count = h // w
	for i in range(count):
		frame = sheet.subsurface(pygame.Rect(0, i * w, w, w)).copy()
		frames.append(frame)
	return frames


def _scale_frames(frames: list[pygame.Surface], size: int) -> list[pygame.Surface]:
	if size <= 0:
		return frames
	out: list[pygame.Surface] = []
	for f in frames:
		w, h = f.get_width(), f.get_height()
		if w <= 0 or h <= 0:
			out.append(f)
			continue
		# Treat `size` as a target HEIGHT. Preserve aspect ratio.
		if h == size:
			out.append(f)
			continue
		new_w = max(1, int(round((w / h) * size)))
		out.append(pygame.transform.scale(f, (new_w, size)))
	return out


def _normalize_frames_bottom_center(frames: list[pygame.Surface]) -> list[pygame.Surface]:
	"""Normalize a frame list so the visible pixels don't 'drift' frame-to-frame.

	Many sprite packs have variable transparent padding, which makes an otherwise
	stationary character look like it's sliding left/right. This function:
	- finds the non-transparent bounding box per frame
	- creates a common canvas sized to the max bounding box
	- blits each cropped frame so its *bottom center* is aligned
	"""
	if not frames:
		return frames

	bounds: list[pygame.Rect] = []
	for f in frames:
		try:
			mask = pygame.mask.from_surface(f)
			rects = mask.get_bounding_rects()
			if not rects:
				bounds.append(pygame.Rect(0, 0, f.get_width(), f.get_height()))
				continue
			x1 = min(r.left for r in rects)
			y1 = min(r.top for r in rects)
			x2 = max(r.right for r in rects)
			y2 = max(r.bottom for r in rects)
			bounds.append(pygame.Rect(x1, y1, x2 - x1, y2 - y1))
		except Exception:
			bounds.append(pygame.Rect(0, 0, f.get_width(), f.get_height()))

	max_w = max(1, max(r.width for r in bounds))
	max_h = max(1, max(r.height for r in bounds))

	out: list[pygame.Surface] = []
	for f, r in zip(frames, bounds):
		canvas = pygame.Surface((max_w, max_h), flags=pygame.SRCALPHA)
		canvas.fill((0, 0, 0, 0))
		try:
			cropped = f.subsurface(r).copy()
		except Exception:
			cropped = f
		# bottom-center align
		dst_x = (max_w - cropped.get_width()) // 2
		dst_y = max_h - cropped.get_height()
		canvas.blit(cropped, (dst_x, dst_y))
		out.append(canvas)
	return out


def _content_bbox(surface: pygame.Surface) -> pygame.Rect:
	"""Return the bounding box of non-transparent pixels (best-effort)."""
	try:
		mask = pygame.mask.from_surface(surface)
		rects = mask.get_bounding_rects()
		if not rects:
			return pygame.Rect(0, 0, surface.get_width(), surface.get_height())
		x1 = min(r.left for r in rects)
		y1 = min(r.top for r in rects)
		x2 = max(r.right for r in rects)
		y2 = max(r.bottom for r in rects)
		return pygame.Rect(x1, y1, max(1, x2 - x1), max(1, y2 - y1))
	except Exception:
		return pygame.Rect(0, 0, surface.get_width(), surface.get_height())


def _scale_frames_by_content_height(frames: list[pygame.Surface], target_content_h: int) -> list[pygame.Surface]:
	"""Crop each frame to its content bbox, then scale so content height == target_content_h."""
	if not frames:
		return frames
	target_content_h = max(1, int(target_content_h))
	out: list[pygame.Surface] = []
	for f in frames:
		bbox = _content_bbox(f)
		try:
			cropped = f.subsurface(bbox).copy()
		except Exception:
			cropped = f
		cw, ch = cropped.get_width(), cropped.get_height()
		if cw <= 0 or ch <= 0:
			out.append(cropped)
			continue
		if ch == target_content_h:
			out.append(cropped)
			continue
		new_w = max(1, int(round((cw / ch) * target_content_h)))
		out.append(pygame.transform.scale(cropped, (new_w, target_content_h)))
	return out


def _normalize_frames_bottom_center_to(frames: list[pygame.Surface], *, canvas_w: int, canvas_h: int) -> list[pygame.Surface]:
	"""Normalize to a provided canvas size (bottom-center aligned)."""
	if not frames:
		return frames
	canvas_w = max(1, int(canvas_w))
	canvas_h = max(1, int(canvas_h))
	out: list[pygame.Surface] = []
	for f in frames:
		canvas = pygame.Surface((canvas_w, canvas_h), flags=pygame.SRCALPHA)
		canvas.fill((0, 0, 0, 0))
		dst_x = (canvas_w - f.get_width()) // 2
		dst_y = canvas_h - f.get_height()
		canvas.blit(f, (dst_x, dst_y))
		out.append(canvas)
	return out


def _load_png(path: str) -> pygame.Surface | None:
	try:
		return pygame.image.load(path).convert_alpha()
	except pygame.error:
		# Can happen during very early init.
		try:
			return pygame.image.load(path)
		except Exception:
			return None
	except Exception:
		return None


def _load_gif_frames(path: str) -> list[pygame.Surface]:
	"""Load GIF frames via Pillow (preferred) with a pygame fallback.

	Pygame typically loads only the first GIF frame.
	"""
	frames: list[pygame.Surface] = []
	try:
		from PIL import Image

		img = Image.open(path)
		for i in range(getattr(img, "n_frames", 1)):
			try:
				img.seek(i)
			except EOFError:
				break
			rgba = img.convert("RGBA")
			data = rgba.tobytes()
			surface = pygame.image.fromstring(data, rgba.size, "RGBA")
			try:
				frames.append(surface.convert_alpha())
			except Exception:
				frames.append(surface)
		return frames
	except Exception:
		# Fallback: at least return the first frame if pygame can load it.
		s = _load_png(path)
		return [s] if s is not None else []


def _load_frames_from_folder(folder: str) -> list[pygame.Surface]:
	if not os.path.isdir(folder):
		return []
	files = [
		f
		for f in os.listdir(folder)
		if f.lower().endswith((".png", ".gif"))
	]
	files.sort(key=_natural_key)

	frames: list[pygame.Surface] = []
	for name in files:
		path = os.path.join(folder, name)
		if name.lower().endswith(".gif"):
			frames.extend(_load_gif_frames(path))
			continue
		img = _load_png(path)
		if img is None:
			continue
		# If it's a strip, split it; otherwise treat it as a single frame.
		split = _split_strip(img)
		if not split:
			split = _split_vertical_strip(img)
		frames.extend(split if split else [img])
	return frames


def _load_strip_or_single(path: str) -> list[pygame.Surface]:
	if not os.path.isfile(path):
		return []
	if path.lower().endswith(".gif"):
		return _load_gif_frames(path)
	img = _load_png(path)
	if img is None:
		return []
	frames = _split_strip(img)
	if not frames:
		frames = _split_vertical_strip(img)
	return frames if frames else [img]


@dataclass(frozen=True)
class TowerSprites:
	idle: dict[str, list[pygame.Surface]]
	attack: dict[str, list[pygame.Surface]]
	projectile: list[pygame.Surface]
	supports_directions: bool


_TOWER_FOLDER_BY_TYPE: dict[str, str] = {
	"goblin": "GOBLIN",
	"elf": "elf",
	"knight": "knight",
	"archer": "ARCHER PURPLE",
	"wizard": "wizard",
	"firewarrior": "FIRE WARRIOR",
	"bloodmage": "blood mage",
}


_TOWER_CACHE: dict[str, TowerSprites] = {}


def _empty_dirs() -> dict[str, list[pygame.Surface]]:
	return {"down": [], "up": [], "left": [], "right": []}


def _ensure_dir_fallbacks(frames_by_dir: dict[str, list[pygame.Surface]]) -> dict[str, list[pygame.Surface]]:
	any_frames = next((v for v in frames_by_dir.values() if v), [])
	if any_frames:
		for k in ("down", "up", "left", "right"):
			if not frames_by_dir.get(k):
				frames_by_dir[k] = list(any_frames)
	return frames_by_dir


def _load_goblin(folder: str) -> TowerSprites:
	idle = _empty_dirs()
	attack = _empty_dirs()
	mapping = {
		"down": ("GoblinIdleDown.png", "GoblinAttackOneDown.png"),
		"up": ("GoblinIdleUp.png", "GoblinAttackOneUp.png"),
		"left": ("GoblinIdleLeft.png", "GoblinAttackOneLeft.png"),
		"right": ("GoblinIdleRight.png", "GoblinAttackOneRight.png"),
	}
	for d, (idle_name, attack_name) in mapping.items():
		idle_path = os.path.join(folder, idle_name)
		attack_path = os.path.join(folder, attack_name)

		idle_img = _load_png(idle_path)
		if idle_img is not None:
			idle[d] = _split_horizontal_equal(idle_img, 3) or [idle_img]
		else:
			idle[d] = []

		attack_img = _load_png(attack_path)
		if attack_img is not None:
			attack[d] = _split_horizontal_equal(attack_img, 4) or [attack_img]
		else:
			attack[d] = []
	return TowerSprites(
		idle=_ensure_dir_fallbacks(idle),
		attack=_ensure_dir_fallbacks(attack),
		projectile=[],
		supports_directions=True,
	)


def _load_wizard(folder: str) -> TowerSprites:
	idle_frames = _load_frames_from_folder(os.path.join(folder, "idle"))
	attack_frames = _load_frames_from_folder(os.path.join(folder, "attack"))
	projectile_frames = _load_frames_from_folder(os.path.join(folder, "green ice cube"))
	idle = {"down": idle_frames, "up": idle_frames, "left": idle_frames, "right": idle_frames}
	attack = {"down": attack_frames, "up": attack_frames, "left": attack_frames, "right": attack_frames}
	return TowerSprites(idle=idle, attack=attack, projectile=projectile_frames, supports_directions=False)


def _load_archer(folder: str) -> TowerSprites:
	# Only a single sheet is provided. Use it for idle and attack.
	sheet = os.path.join(folder, "GandalfHardcore Archer purple sheet.png")
	frames = _load_strip_or_single(sheet)
	projectile_frames = _load_frames_from_folder(os.path.join(folder, "arrow"))
	idle = {"down": frames, "up": frames, "left": frames, "right": frames}
	attack = {"down": frames, "up": frames, "left": frames, "right": frames}
	return TowerSprites(idle=idle, attack=attack, projectile=projectile_frames, supports_directions=False)


def _load_knight(folder: str) -> TowerSprites:
	idle_dir = os.path.join(folder, "war idle")
	idle_frames = []
	if os.path.isdir(idle_dir):
		# Prefer individual 32x32 frames over the huge spritesheet.
		files = [f for f in os.listdir(idle_dir) if f.lower().endswith(".png") and "war-idle" in f.lower()]
		files.sort(key=_natural_key)
		for f in files:
			img = _load_png(os.path.join(idle_dir, f))
			if img is not None:
				idle_frames.append(img)
		if not idle_frames:
			idle_frames = _load_frames_from_folder(idle_dir)

	attack_frames = []
	attack_dir = os.path.join(folder, "war attack")
	if os.path.isdir(attack_dir):
		attack_files = [
			f for f in os.listdir(attack_dir)
			if f.lower().endswith(".png") and "war-attack" in f.lower()
		]
		attack_files.sort(key=_natural_key)
		for f in attack_files:
			img = _load_png(os.path.join(attack_dir, f))
			if img is not None:
				attack_frames.append(img)
	else:
		# Older layout (attack frames at the knight root)
		attack_files = [f for f in os.listdir(folder) if f.lower().endswith(".png") and "war-attack" in f.lower()]
		attack_files.sort(key=_natural_key)
		for f in attack_files:
			img = _load_png(os.path.join(folder, f))
			if img is not None:
				attack_frames.append(img)

	# Knight art is inconsistent: many attack frames include extra transparent padding,
	# which makes the knight look smaller if we scale by the full surface height.
	# Fix: scale by *content height* (non-transparent bbox), then normalize both sets
	# into the same canvas so attack/idle remain the same visual size.
	if idle_frames:
		ref_h = max(_content_bbox(f).height for f in idle_frames)
	elif attack_frames:
		ref_h = max(_content_bbox(f).height for f in attack_frames)
	else:
		ref_h = 32

	idle_scaled = _scale_frames_by_content_height(idle_frames, ref_h)
	attack_scaled = _scale_frames_by_content_height(attack_frames, ref_h)

	# Normalize both sets into a shared canvas to avoid drift.
	all_for_canvas = [*idle_scaled, *attack_scaled] or idle_scaled or attack_scaled
	if all_for_canvas:
		canvas_w = max(f.get_width() for f in all_for_canvas)
		canvas_h = max(f.get_height() for f in all_for_canvas)
	else:
		canvas_w, canvas_h = 1, 1

	idle_norm = _normalize_frames_bottom_center_to(idle_scaled, canvas_w=canvas_w, canvas_h=canvas_h)
	attack_norm = _normalize_frames_bottom_center_to(attack_scaled, canvas_w=canvas_w, canvas_h=canvas_h)

	idle = {"down": idle_norm, "up": idle_norm, "left": idle_norm, "right": idle_norm}
	attack = {"down": attack_norm, "up": attack_norm, "left": attack_norm, "right": attack_norm}
	return TowerSprites(idle=idle, attack=attack, projectile=[], supports_directions=False)


def _load_fire_warrior(folder: str) -> TowerSprites:
	# These sheets are non-square frames:
	# - idle.png: 768x64 => 6 frames of 128x64
	# - attack.png: 512x64 => 4 frames of 128x64
	idle_img = _load_png(os.path.join(folder, "idle.png"))
	attack_img = _load_png(os.path.join(folder, "attack.png"))

	idle_frames: list[pygame.Surface] = []
	attack_frames: list[pygame.Surface] = []
	if idle_img is not None:
		idle_frames = _split_horizontal_equal(idle_img, 6) or [idle_img]
	if attack_img is not None:
		attack_frames = _split_horizontal_equal(attack_img, 4) or [attack_img]

	# Normalize to prevent drift from uneven padding.
	idle_frames = _normalize_frames_bottom_center(idle_frames)
	attack_frames = _normalize_frames_bottom_center(attack_frames)
	idle = {"down": idle_frames, "up": idle_frames, "left": idle_frames, "right": idle_frames}
	attack = {"down": attack_frames, "up": attack_frames, "left": attack_frames, "right": attack_frames}
	return TowerSprites(idle=idle, attack=attack, projectile=[], supports_directions=False)


def _load_elf(folder: str) -> TowerSprites:
	# These are GIFs only; use Pillow to animate.
	idle_frames = _load_strip_or_single(os.path.join(folder, "elf_Idle.gif"))

	attack_candidates = [
		os.path.join(folder, "elf_attack_3hit_forward.gif"),
		os.path.join(folder, "elf_attack_1hit_v2.gif"),
		os.path.join(folder, "elf_attack_1hit.gif"),
	]
	attack_frames: list[pygame.Surface] = []
	for c in attack_candidates:
		attack_frames = _load_strip_or_single(c)
		if attack_frames:
			break
	idle = {"down": idle_frames, "up": idle_frames, "left": idle_frames, "right": idle_frames}
	attack = {"down": attack_frames, "up": attack_frames, "left": attack_frames, "right": attack_frames}
	return TowerSprites(idle=idle, attack=attack, projectile=[], supports_directions=False)


def _load_blood_mage(folder: str) -> TowerSprites:
	# Use GIFs for blood mage to avoid the Demo sheet containing multiple copies per frame.
	idle_frames = _load_strip_or_single(os.path.join(folder, "idle.gif"))
	if not idle_frames:
		idle_frames = _load_strip_or_single(os.path.join(folder, "Demo.png"))

	# Prefer a casting attack gif if present.
	attack_candidates = [
		os.path.join(folder, "cast spell.gif"),
		os.path.join(folder, "meelee attack.gif"),
	]
	attack_frames: list[pygame.Surface] = []
	for c in attack_candidates:
		attack_frames = _load_strip_or_single(c)
		if attack_frames:
			break

	# Projectiles come from the dedicated folder.
	projectile_frames = _load_frames_from_folder(os.path.join(folder, "shadow ball"))
	idle = {"down": idle_frames, "up": idle_frames, "left": idle_frames, "right": idle_frames}
	attack = {"down": attack_frames, "up": attack_frames, "left": attack_frames, "right": attack_frames}
	return TowerSprites(idle=idle, attack=attack, projectile=projectile_frames, supports_directions=False)


def get_tower_sprites(tower_type: str, *, tower_size: int) -> TowerSprites:
	"""Return cached and scaled tower sprites for a given tower type."""
	tower_type = (tower_type or "").lower()
	folder_name = _TOWER_FOLDER_BY_TYPE.get(tower_type)
	if not folder_name:
		return TowerSprites(idle=_empty_dirs(), attack=_empty_dirs(), projectile=[], supports_directions=False)

	cache_key = f"{tower_type}@{tower_size}"
	if cache_key in _TOWER_CACHE:
		return _TOWER_CACHE[cache_key]

	folder = os.path.join(_TOWER_ROOT, folder_name)
	if not os.path.isdir(folder):
		sprites = TowerSprites(idle=_empty_dirs(), attack=_empty_dirs(), projectile=[], supports_directions=False)
		_TOWER_CACHE[cache_key] = sprites
		return sprites

	if tower_type == "goblin":
		sprites = _load_goblin(folder)
	elif tower_type == "wizard":
		sprites = _load_wizard(folder)
	elif tower_type == "archer":
		sprites = _load_archer(folder)
	elif tower_type == "knight":
		sprites = _load_knight(folder)
	elif tower_type == "firewarrior":
		sprites = _load_fire_warrior(folder)
	elif tower_type == "elf":
		sprites = _load_elf(folder)
	elif tower_type == "bloodmage":
		sprites = _load_blood_mage(folder)
	else:
		sprites = TowerSprites(idle=_empty_dirs(), attack=_empty_dirs(), projectile=[], supports_directions=False)

	# Scale everything to requested tower_size.
	idle_scaled = {k: _scale_frames(list(v), tower_size) for k, v in sprites.idle.items()}
	attack_scaled = {k: _scale_frames(list(v), tower_size) for k, v in sprites.attack.items()}
	proj_scaled = _scale_frames(list(sprites.projectile), max(1, tower_size // 2))
	scaled = TowerSprites(
		idle=idle_scaled,
		attack=attack_scaled,
		projectile=proj_scaled,
		supports_directions=sprites.supports_directions,
	)
	_TOWER_CACHE[cache_key] = scaled
	return scaled


def get_projectile_frames(source_type: str, *, projectile_size: int) -> list[pygame.Surface]:
	source_type = (source_type or "").lower()
	# In get_tower_sprites, projectile frames are scaled to tower_size//2.
	# So we request tower_size=projectile_size*2 to receive projectiles at the
	# requested projectile_size directly.
	sprites = get_tower_sprites(source_type, tower_size=max(1, projectile_size * 2))
	return list(sprites.projectile)
