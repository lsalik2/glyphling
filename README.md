# glyphling

A procedurally-generated, interactive ASCII pet that lives in your terminal — a one-of-a-kind creature you care for that reacts to your real dev life.

> **Note:** the project is named **glyphling**, but the CLI command is currently `asciipet` (the rename to `glyphling` is on the roadmap below).

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

## Roadmap

glyphling grows in layers — each phase stands on its own, so it's always a whole thing, never half-built.

**✅ Shipped — v0.1 · "the pet is alive"**
- Procedural generation — a unique look, temperament, quirks, and species rules from a single seed
- Care simulation — five needs, derived moods, life stages, bond; *suffers but survives* (it can never die)
- Real-time decay with offline catch-up, saved between sessions
- Animated Textual TUI — feed · play · clean · rest · pet · rename

**⏳ Next up**
- Rename `asciipet` → `glyphling` (package, CLI, repo)
- **Phase 2 · "it lives on its own"** — a lightweight background daemon plus zero-setup ambient sensors (system vitals, time-of-day & circadian rhythm), so your pet keeps living — sleeping at night, stirring by day — even when the window's closed

**🗺️ Planned**
- **Phase 3 · "desk familiar"** — an opt-in shell hook so glyphling reacts to your real dev life: cheers green tests, celebrates commits, winces at errors, perks up when you return. *Privacy-first: command names only, never keystrokes; fully opt-in and removable.*
- **Phase 4 · polish & breadth** — a one-line status-bar/tmux view, more archetypes/parts/quirks, visible life-stage growth, bond payoffs, color themes, balance tuning

### 🌱 Beyond Phase 4 — expansion ideas

Directions glyphling could grow once the core is solid. Nothing scheduled — this is the fun horizon.

**More creatures**
- New archetypes / body plans — aquatic, avian, serpentine, plant·mossling, insectoid, slime, crystalline, mechanical, ghost·wisp, mythic (dragon / phoenix)
- Rare & "shiny" variants — uncommon seeds yield special palettes, parts, or markings
- Elemental & biome themes — fire / water / earth / air flavors that shape both looks *and* behavior
- Expanded palettes, patterns & animated textures
- Wearable cosmetics — hats, scarves, tiny found objects
- Seasonal & event creatures — special generation around holidays

**Deeper personality**
- More temperament axes + emergent "personality archetypes" (the grump, the cuddlebug, the daydreamer)
- Personality drift — how you treat it gradually shapes who it becomes (nurture bends nature)
- Memories & preferences — favorite foods, favorite time of day, little callbacks to shared moments
- Dreams while sleeping — brief dream vignettes
- A growing, personality-flavored vocabulary of lines and reactions

**Richer care & play**
- Mini-games — fetch, hide-and-seek, a tiny terminal game or two
- Foods, toys & items tied to species diet and mood
- Learnable tricks unlocked by bond
- Achievements & milestones — first week, 100 tests cheered, bond tiers
- Care-shaped growth — life-stage outcomes branch on how you raised it

**More companion integrations**
- Extra sensors — git branch, CI status, calendar/meetings ("quiet mode"), now-playing, focus/pomodoro timers
- Cross-shell hooks — fish, nushell, PowerShell
- Gentle, opt-in notifications — "time to stretch", "your pet missed you"

**Make it yours**
- UI themes / skins
- A data-driven mod system — author your own parts, foods, quirks, and reactions
- An ambient "screensaver" mode
- Accessibility — pure-ASCII, no-color, screen-reader-friendly modes

**Social**
- Shareable creature seeds & exportable "creature cards"
- Async "visits" — send your creature to a friend's terminal
- Collection & breeding with inherited traits; a small interacting household
- A community gallery of seeds
