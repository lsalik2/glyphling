# asciipet

A procedurally-generated, interactive ASCII pet that lives in your terminal.

## Install
```
pip install -e ".[dev]"
```

## Use
- `asciipet hatch 42` — preview the creature a seed produces
- `asciipet` — hatch (first run) and open your pet's live view
- `asciipet rename Pixel` — rename your pet

In the live view: **f** feed · **p** play · **c** clean · **r** rest · **e** pet · **n** rename · **q** quit.

Your pet is saved at `$XDG_DATA_HOME/asciipet/pet.json` and keeps living (gently) while you're away.
