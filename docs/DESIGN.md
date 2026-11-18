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

## Initial Implementation Decisions

### Turn Order
- Each round uses a fixed turn order:
  Player 1, Player 2, Player 3, Enemy 1, Enemy 2.
- Each living character may attack once per round.
- Defeated characters skip their turns.
- A new round begins after all eligible characters
  have had their turn.
- Combat ends immediately when either team is defeated.

### Targeting
- Every attack must specify a target.
- Targets must be living characters on the opposing team.
- Both player and enemy actions receive manually
  specified targets for now.
- No automatic enemy targeting or AI is required.
- Callers may query legal targets with
  Battle.valid_targets(attacker):
  - Returns a new list of existing Character
    references for living opposing-team participants.
  - Preserves the opposing team's roster order.
  - Valid only while the battle is ongoing and
    attacker is the current actor (object identity).
  - Raises InvalidActionError for invalid callers,
    including after the battle has ended.
  - Does not modify HP, turn order, round number,
    battle outcome, or other battle state.
  - Does not automatically select a target or
    perform an attack.
- Callers may query legal attack options with
  Battle.turn_options(attacker):
  - Read-only overview of the current actor's
    legal targets and predicted attack outcomes.
  - Valid only while the battle is ongoing and
    attacker is the current actor (object identity).
  - Raises InvalidActionError for invalid callers,
    including after the battle has ended.
  - Returns List[Dict[str, Any]] in the same
    opposing-team roster order as valid_targets.
  - Each dict contains exactly: target, damage,
    target_hp_after, and would_defeat.
  - target is the original live Character reference
    (same object identity as from valid_targets).
  - damage, target_hp_after, and would_defeat match
    preview_attack(attacker, target).
  - Implementation reuses valid_targets and
    preview_attack directly.
  - Returns a fresh list and fresh dictionaries
    on each call.
  - An empty list is permitted if valid_targets
    returns no targets.
  - Does not modify HP, turn order, round number,
    battle outcome, or other battle state.
  - Does not automatically select a target, rank
    options, perform an attack, or introduce new
    mechanics.
  - Returned Character references remain live and
    can be mutated by callers; the query itself
    must not mutate them.

### Combat Rules
- Attacks deal fixed damage equal to the
  attacker's attack stat.
- Damage cannot be negative.
- HP cannot fall below 0.
- Defeated characters cannot attack.
- Invalid actions must be rejected.
- No critical hits, healing, shields, or randomness.

### Starting Statistics
Player 1: 30 HP, 10 attack
Player 2: 25 HP, 12 attack
Player 3: 35 HP, 8 attack

Enemy 1: 25 HP, 7 attack
Enemy 2: 25 HP, 7 attack

These are example values for testing, not
final game-balance decisions.

### Implementation
- Use Python 3 and standard libraries only.
- Build reusable combat logic.
- Use unittest for automated tests.
- No GUI or CLI is required initially.
- Combat actions will be supplied by test code.
- Keep the implementation simple and modular.

### Victory and Defeat
- Victory occurs immediately when all enemies die.
- Defeat occurs immediately when all players die.
- Simultaneous defeat is not possible under
  the current sequential damage rules.
