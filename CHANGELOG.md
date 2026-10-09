# Changelog

All notable changes to glyphling are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Release engineering: single-source version (`glyphling.__version__`), this changelog,
  CI across Linux/macOS and Python 3.11–3.14, and a PyPI Trusted Publishing workflow.

## [0.2.0] - 2026-06-18

### Added
- Background daemon (`glyphling daemon start/stop/status`) with ambient sensors: circadian
  sleep and a mood tint from CPU/battery load while the TUI is closed.
- Opt-in shell hook (`glyphling shell-init`) and dev-activity reactions — cheers tests,
  celebrates commits, winces at failures, startles at scary commands — with speech bubbles
  and a welcome-back greeting.
- Life-stage- and personality-aware need decay; quirks wired to behavior; bond tiers
  (stranger → bonded) that soften gloom and warm greetings.
- `glyphling status` one-line glance (`--compact` for the short form).
- Seeded per-creature color palette that mood-tints; monochrome under `NO_COLOR`,
  non-truecolor terminals, or when piped.
- Visible life-stage growth: a shared egg hatches and grows through baby, juvenile, adult,
  and elder.
- Six body plans: blob, critter, avian, serpentine, quadruped, tuft.

## [0.1.0] - 2026-06-14

### Added
- Procedural creature generation from a seed: look, temperament, quirks, species rules.
- Care simulation: five needs, derived moods, life stages, bond; the pet suffers but never dies.
- Real-time decay with offline catch-up and atomic saves.
- Animated Textual TUI (feed · play · clean · rest · pet · rename) and the `glyphling`,
  `glyphling hatch`, and `glyphling rename` commands.
