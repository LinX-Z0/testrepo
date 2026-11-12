# Turn-Based Combat Simulator

## Project Goal
Build a small Python combat simulator to experiment
with AI-assisted programming and automated testing.

## Core Mechanics

### Characters
- The player controls 3 characters.
- Each character has HP and attack damage.
- A character is defeated when HP reaches 0.

### Combat
- Combat is turn-based.
- Each living character may attack once per round.
- An attack reduces the target's HP.
- HP cannot fall below 0.
- Defeated characters cannot perform actions.

### Enemies
- The enemy team consists of 2 enemies.
- Enemies have HP and attack damage.
- Enemies follow the same basic attack rules.

### Victory
- The player wins when all enemies are defeated.
- The player loses when all player characters
  are defeated.

## Initial Scope
- Python only.
- No graphical interface.
- No external libraries.
- Deterministic combat logic.
- Unit tests for combat rules.

## Future Features
- 3x3 positioning grid.
- Formation bonuses.
- Character abilities.
- Simple enemy AI.

These are NOT part of the initial implementation.

## Development Rules
- Follow AGENTS.md.
- Implement features incrementally.
- Add automated tests for core rules.
- Do not introduce unspecified game mechanics.
