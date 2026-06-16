from glyphling.core.spec import CreatureSpec
from glyphling.core import parts, quirks

def _c(rgb) -> str:
    return f"rgb({rgb[0]},{rgb[1]},{rgb[2]})"

def _esc(s: str) -> str:
    """Make literal text safe inside Rich color tags without importing Rich. Body templates and
    system speech contain no '[' (no tag-injection), but the critter lines END with '\\'; a
    trailing backslash would escape a following '[/]' close tag. Pad an ODD trailing run of
    backslashes to even, which Rich then reads as literal backslashes followed by a real tag."""
    trailing = len(s) - len(s.rstrip("\\"))
    return s + "\\" if trailing % 2 == 1 else s

def _add_sleep_z(art: str, frame_idx: int) -> str:
    z = ["  z", "   z", "  Z"][frame_idx % 3]
    lines = art.split("\n")
    lines[0] = lines[0] + z
    return "\n".join(lines)

def _add_speech(text: str) -> str:
    return f"( {text} )"

def render(spec: CreatureSpec, mood: str, frame_idx: int = 0, speech: str = "", palette=None) -> str:
    template = parts.BODY_TEMPLATES[spec.species.archetype.value]
    eye_override, mouth_override = parts.MOOD_FACE.get(mood, (None, None))
    eyes = eye_override if eye_override is not None else spec.body.eyes
    mouth = mouth_override if mouth_override is not None else spec.body.mouth

    # Blink: every 4th frame while awake.
    if mood != "sleeping" and frame_idx % 4 == 3:
        eyes = "- -"

    if mood == "sleeping" and quirks.has_pose_quirk(spec, "upside_down"):
        eyes, mouth = "v v", "^"   # intentionally ASCII (the pet is pure-ASCII), not a unicode glyph

    if palette is not None:
        eyes = f"[{_c(palette.eyes)}]{eyes}[/]"
        mouth = f"[{_c(palette.accent)}]{mouth}[/]"
        # Escape the literal template (not the eyes/mouth markup we just built) before wrapping.
        art_lines = [f"[{_c(palette.body)}]{_esc(line).format(eyes=eyes, mouth=mouth)}[/]" for line in template]
    else:
        art_lines = [line.format(eyes=eyes, mouth=mouth) for line in template]
    art = "\n".join(art_lines)
    if mood == "sleeping":
        art = _add_sleep_z(art, frame_idx)

    # Always reserve the top line for the speech bubble (blank when silent) so the
    # creature never jumps up/down a row when a reaction pops or fades.
    if speech:
        if palette is not None:
            bubble = f"[dim {_c(palette.eyes)}]{_add_speech(_esc(speech))}[/]"
        else:
            bubble = _add_speech(speech)
    else:
        bubble = ""
    return bubble + "\n" + art
