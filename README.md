# glyphling

A procedurally-generated, interactive ASCII pet that lives in your terminal — a one-of-a-kind creature you care for that reacts to your real dev life.

## Install
```
pipx install git+https://github.com/lsalik2/glyphling    # isolated, recommended
# or, from a clone for development:
pip install -e ".[dev]"
```

## Use
- `glyphling hatch 42` — preview the creature a seed produces
- `glyphling` — hatch (first run) and open your pet's live view
- `glyphling rename Pixel` — rename your pet
- `glyphling status` — a one-line glance at your pet (great in a shell prompt or tmux status bar; `--compact` for the short form)

In the live view: **f** feed · **p** play · **c** clean · **r** rest · **e** pet · **n** rename · **q** quit.

Your pet is saved at `$XDG_DATA_HOME/glyphling/pet.json` and keeps living (gently) while you're away. State is written atomically, with a `.bak` kept for recovery; the state directory and files are created user-only (`0700`/`0600`).

> **One ticker at a time.** With no daemon running, the open live view ticks the simulation itself — so run a single view at a time (two owner-mode views would both tick and the last save would win). A running daemon is the single source of truth, and any number of views can safely watch it as readers.

### Keep it alive in the background (optional)
- `glyphling daemon start` — run the companion in the background (it keeps living while the TUI is closed)
- `glyphling daemon status` — check whether it's running
- `glyphling daemon stop` — stop it

For an always-on pet, add this to your shell rc (`~/.bashrc` / `~/.zshrc`):

```
glyphling daemon start >/dev/null 2>&1
```

With the daemon running, your glyphling sleeps on its circadian schedule (diurnal / nocturnal / crepuscular) and is ambiently tinted by your machine's load — visible whenever you open the live view.

### Make it a desk familiar (optional)
Let your pet react to your dev life — cheering green tests, celebrating commits, wincing at
failures, startling at scary commands, and greeting you when you return:

1. `glyphling daemon start` (it watches while it runs)
2. `glyphling shell-init >> ~/.bashrc` (or `~/.zshrc`), then restart your shell

**Privacy:** fully opt-in. The hook logs only the command lines you run (already in your shell
history) plus exit codes — never keystrokes typed into programs. The log is local, drained
continuously, and you can delete it or remove the hook block anytime. glyphling makes no network
calls, ever.

## Roadmap

glyphling grows in layers — each phase stands on its own, so it's always a whole thing, never half-built.

**✅ Shipped — v0.1 · "the pet is alive"**
- Procedural generation — a unique look, temperament, quirks, and species rules from a single seed
- Care simulation — five needs, derived moods, life stages, bond; *suffers but survives* (it can never die)
- Real-time decay with offline catch-up, saved between sessions
- Animated Textual TUI — feed · play · clean · rest · pet · rename
- Named the project **glyphling** (package, CLI, and repo)
- **Phase 2 — it lives on its own:** background daemon (`glyphling daemon start/stop/status`) + ambient sensors; sleeps at its circadian night, ambient mood from CPU/battery, all while the TUI is closed
- **Phase 3 — desk familiar:** opt-in shell hook (`glyphling shell-init`) + dev-activity reactions (cheers tests, celebrates commits, winces at failures, startles at scary commands) with speech bubbles, plus a welcome-back greeting
- **Phase 4a — depth & payoff:** life-stage- and personality-aware need decay; quirks wired to behavior (idle flourishes, event reactions, an upside-down sleep); bond now pays off — named tiers (stranger → bonded) that soften gloom, warm greetings, and surface favorite quirks; plus a one-line `glyphling status` glance
- **Phase 4b-i — color:** every creature now has a seeded, intrinsic color palette (body · accent · eyes) that mood-tints — a sick pet greys and greens, a sleeping one dims; falls back to clean monochrome under `NO_COLOR`, non-truecolor terminals, or when piped
- **Phase 4b-ii — life-stage growth:** the creature now visibly grows — a shared egg hatches into a tiny big-eyed baby and grows through juvenile, adult, and a wispy elder, per archetype (color and mood ride along at every stage)
- **Phase 4b-iii — more creatures:** six body plans now — blob, critter, avian, serpentine, quadruped, tuft — each with its own egg→elder growth and color. Adding creatures keeps your existing pet exactly as it is (its type is saved on disk); a given seed keeps its name/personality/quirks, though its shape may differ from before

**⏳ Next up**
- **Beyond Phase 4** — see the expansion ideas below

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

## License

MIT — see [LICENSE](LICENSE).
