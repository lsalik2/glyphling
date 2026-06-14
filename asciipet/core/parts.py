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
}

# Deterministic cute-name syllables.
NAME_ONSETS = ["m", "p", "q", "b", "t", "s", "r", "n", "l", "g"]
NAME_VOWELS = ["o", "e", "a", "i", "u", "or", "ee", "oo"]
NAME_CODAS = ["ss", "back", "lim", "ra", "x", "rt", "n", "th"]
