from glyphling.core.spec import CreatureSpec
from glyphling.core import parts, quirks

def _add_sleep_z(art: str, frame_idx: int) -> str:
    z = ["  z", "   z", "  Z"][frame_idx % 3]
    lines = art.split("\n")
    lines[0] = lines[0] + z
    return "\n".join(lines)

def _add_speech(text: str) -> str:
    return f"( {text} )"

def render(spec: CreatureSpec, mood: str, frame_idx: int = 0, speech: str = "") -> str:
    template = parts.BODY_TEMPLATES[spec.species.archetype.value]
    eye_override, mouth_override = parts.MOOD_FACE.get(mood, (None, None))
    eyes = eye_override if eye_override is not None else spec.body.eyes
    mouth = mouth_override if mouth_override is not None else spec.body.mouth

    # Blink: every 4th frame while awake.
    if mood != "sleeping" and frame_idx % 4 == 3:
        eyes = "- -"

    if mood == "sleeping" and quirks.has_pose_quirk(spec, "upside_down"):
        eyes, mouth = "v v", "^"   # intentionally ASCII (the pet is pure-ASCII), not a unicode glyph

    art = "\n".join(line.format(eyes=eyes, mouth=mouth) for line in template)
    if mood == "sleeping":
        art = _add_sleep_z(art, frame_idx)
    # Always reserve the top line for the speech bubble (blank when silent) so the
    # creature never jumps up/down a row when a reaction pops or fades.
    bubble = _add_speech(speech) if speech else ""
    return bubble + "\n" + art
