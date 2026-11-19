# Combat Simulator

A small deterministic Python combat simulator. It models turn-based battles between a player team and an enemy team. There is no graphical interface, no command-line entry point, and no external libraries. Callers supply each attack; the included tests exercise the rules.

## What it does

Each battle has exactly three player characters and two enemy characters. A character has a name, hit points (HP), a fixed attack value, and a team (`player` or `enemy`). A character is defeated when HP reaches 0. Starting HP and attack cannot be negative.

Combat proceeds in rounds with a fixed turn order: the player roster, then the enemy roster. For the default battle that order is Player 1, Player 2, Player 3, Enemy 1, Enemy 2. Each living character may attack once per round. Defeated characters skip their turns. A new round begins when the turn order wraps.

An attack deals damage equal to the attacker's attack stat. Damage cannot be negative, and HP cannot fall below 0. The target must be a living participant on the opposing team. Player and enemy attacks both use a target chosen by the caller. The simulator does not choose targets automatically and does not include enemy AI.

`Battle.attack` resolves one legal attack and advances the turn. An illegal attack raises `InvalidActionError` and leaves HP, turn order, round number, and outcome unchanged. The battle ends immediately when one team is fully defeated: `victory` when every enemy is defeated, and `defeat` when every player character is defeated. Until then the outcome is `ongoing`.

These read-only queries do not change battle state:

- `valid_targets` lists living opponents of the current actor, in opposing-team roster order.
- `preview_attack` predicts damage, the target's HP after the attack (not below 0), and whether that attack would defeat the target.
- `turn_options` returns each legal target with that same prediction (`target`, `damage`, `target_hp_after`, and `would_defeat`).
- `snapshot` returns a plain copy of the current round, outcome, actor, and character stats.

`create_default_battle()` uses the example starting statistics from the design document:

| Character | HP | Attack |
| --- | ---: | ---: |
| Player 1 | 30 | 10 |
| Player 2 | 25 | 12 |
| Player 3 | 35 | 8 |
| Enemy 1 | 25 | 7 |
| Enemy 2 | 25 | 7 |

Those values are examples for testing, not final balance decisions.

The design lists later ideas that this code does not implement: a 3x3 positioning grid, formation bonuses, character abilities, and enemy AI. The current rules also have no critical hits, healing, shields, or randomness.

## Python

The approved design requires Python 3 and the standard library only. This repository does not declare a more specific minimum version.

## Project structure

```
AGENTS.md                 Instructions for AI agents working in this repository
combat/                   Combat package
  __init__.py             Public exports
  models.py               Character and Team
  combat.py               Damage application and single-attack resolution
  battle.py               Turn order, targeting, outcomes, and the default battle
docs/DESIGN.md            Approved gameplay requirements
tests/                    unittest modules for the combat rules
.agents/skills/           Review procedures for agents
  game-system-review/
  independent-implementation-review/
.gitignore                Ignores Python bytecode and virtual environments
```

## Running tests

From the repository root, using Python's standard `unittest` module:

```sh
python3 -m unittest discover -s tests
```

The same discovery command can be run without writing bytecode caches:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
```

## Repository guidance

- `AGENTS.md` tells AI agents how to work here: inspect the repository before editing, treat the approved design as the source of truth, verify changes with the existing tests, and avoid unrelated or unsafe edits.
- `docs/DESIGN.md` is the approved game design. It defines the combat rules in scope and lists future features that are outside the current implementation.
- `.agents/skills/game-system-review/` reviews gameplay design. It evaluates whether a system delivers its intended player experience, including decisions, risk and reward, strategic depth, exploits, and complexity. It does not change files unless asked.
- `.agents/skills/independent-implementation-review/` reviews an implementation in read-only fashion. It compares code and tests with an approved contract and the stated change scope. In this repository that contract is `docs/DESIGN.md`. It judges implementation evidence separately from the design-quality review above.
