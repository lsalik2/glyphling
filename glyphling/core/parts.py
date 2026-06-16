"""Single source of creature data, consumed by generator (choices) and renderer (drawing)."""

EYE_VARIANTS = ["o o", "O O", "- -", "^ ^", "u u", "* *"]
MOUTH_VARIANTS = ["v", "w", "-", "u", "o"]
EARS_VARIANTS = ["^^", "''", "..", "~~"]
PATTERN_VARIANTS = ["plain", "spotted", "striped", "mottled"]

QUIRK_POOL = [
    "chases its tail", "sleeps upside-down", "hums to itself",
    "collects pebbles", "sneezes when startled", "headbangs to fast typing",
]

PERSONALITY_AXES = ("bold", "energy", "affection", "curiosity", "tidy", "playful")

# Body templates: lists of lines with {eyes} and {mouth} slots.
BODY_TEMPLATES = {
    "blob": [
        '   .-"""-.',
        "  ( {eyes} )",
        "  (  {mouth}  )",
        "   `-.__.-'",
    ],
    "critter": [
        "    /\\_/\\",
        "   ( {eyes} )",
        "    > {mouth} <",
        "   /     \\",
    ],
}

# Shared dormant egg (no face slots — .format leaves it untouched).
EGG_TEMPLATE = [
    "   .-.",
    "  ( . )",
    "   `-'",
]

# Per-archetype, per-stage body templates. "adult" reuses BODY_TEMPLATES (byte-identical).
STAGE_TEMPLATES = {
    "blob": {
        "baby": [
            "  ( {eyes} )",
            "   `-{mouth}-'",
        ],
        "juvenile": [
            '   .-"-.',
            "  ( {eyes} )",
            "   `-{mouth}-'",
        ],
        "adult": BODY_TEMPLATES["blob"],
        "elder": [
            "   .-~~~-.",
            "  ( {eyes} )",
            "  (  {mouth}  )",
            "   `-.__.-'",
        ],
    },
    "critter": {
        "baby": [
            "  ( {eyes} )",
            "   > {mouth} <",
        ],
        "juvenile": [
            "   /\\_/\\",
            "  ( {eyes} )",
            "   > {mouth} <",
        ],
        "adult": BODY_TEMPLATES["critter"],
        "elder": [
            "    /\\_/\\",
            "   ( {eyes} )",
            "  ~> {mouth} <~",
            "   /     \\",
        ],
    },
}


def template_for(archetype: str, stage: str) -> list:
    """Body template for an (archetype, stage). Egg is shared; unknown stages fall back to adult."""
    if stage == "egg":
        return EGG_TEMPLATE
    stages = STAGE_TEMPLATES[archetype]
    return stages.get(stage, stages["adult"])


# Mood -> (eyes_override, mouth_override). None means "keep the creature's base part".
MOOD_FACE = {
    "content":  (None, None),
    "happy":    ("^ ^", "w"),
    "excited":  ("O O", "o"),
    "playful":  ("^ ^", "w"),
    "hungry":   (None, "o"),
    "tired":    ("- -", "-"),
    "lonely":   ("u u", "-"),
    "grumpy":   (">_<", "-"),
    "sad":      ("x x", "n"),
    "sick":     ("@ @", "~"),
    "sleeping": ("- -", "u"),
    "startled": ("O O", "O"),
}

# Deterministic cute-name syllables.
NAME_ONSETS = ["m", "p", "q", "b", "t", "s", "r", "n", "l", "g"]
NAME_VOWELS = ["o", "e", "a", "i", "u", "or", "ee", "oo"]
NAME_CODAS = ["ss", "back", "lim", "ra", "x", "rt", "n", "th"]
