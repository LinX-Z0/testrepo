"""Battle orchestration: turn order, targeting, and win/lose checks."""

from enum import Enum
from typing import List, Optional, Sequence

from combat.combat import InvalidActionError, resolve_attack
from combat.models import Character, Team


class BattleOutcome(Enum):
    """Current result of a battle."""

    ONGOING = "ongoing"
    VICTORY = "victory"
    DEFEAT = "defeat"


class Battle:
    """Turn-based battle with three players and two enemies.

    Fixed turn order each round:
    Player 1, Player 2, Player 3, Enemy 1, Enemy 2
    (list order of ``players`` then ``enemies``).
    """

    def __init__(
        self,
        players: Sequence[Character],
        enemies: Sequence[Character],
    ) -> None:
        if len(players) != 3:
            raise ValueError("Battle requires exactly 3 player characters")
        if len(enemies) != 2:
            raise ValueError("Battle requires exactly 2 enemy characters")
        if any(c.team != Team.PLAYER for c in players):
            raise ValueError("All player characters must be on Team.PLAYER")
        if any(c.team != Team.ENEMY for c in enemies):
            raise ValueError("All enemy characters must be on Team.ENEMY")

        self.players: List[Character] = list(players)
        self.enemies: List[Character] = list(enemies)
        self._participants: List[Character] = self.players + self.enemies

        # Fixed order: players[0..2], then enemies[0..1].
        self._turn_order: List[Character] = list(self._participants)

        self.round_number = 1
        self._turn_index = 0
        self._outcome = BattleOutcome.ONGOING
        self._update_outcome()
        if not self.is_over:
            self._skip_defeated_actors()

    @property
    def outcome(self) -> BattleOutcome:
        return self._outcome

    @property
    def is_over(self) -> bool:
        return self._outcome != BattleOutcome.ONGOING

    def current_actor(self) -> Optional[Character]:
        """The living character whose turn it is, or None if the battle is over."""
        if self.is_over:
            return None
        return self._turn_order[self._turn_index]

    def living_players(self) -> List[Character]:
        return [c for c in self.players if c.is_alive]

    def living_enemies(self) -> List[Character]:
        return [c for c in self.enemies if c.is_alive]

    def attack(self, attacker: Character, target: Character) -> None:
        """Resolve one attack for the current actor against a valid target.

        Invalid actions raise InvalidActionError and leave state unchanged.
        """
        if self.is_over:
            raise InvalidActionError("Battle is already over")

        current = self.current_actor()
        if attacker is not current:
            raise InvalidActionError(
                f"It is not {attacker.name}'s turn "
                f"(current actor is {current.name if current else None})"
            )

        self._validate_target(attacker, target)

        # All checks passed; apply damage then update battle state.
        resolve_attack(attacker, target)

        self._update_outcome()
        if self.is_over:
            return

        self._advance_turn()

    def _validate_target(self, attacker: Character, target: Character) -> None:
        if target not in self._participants:
            raise InvalidActionError("Target is not a participant in this battle")
        if not target.is_alive:
            raise InvalidActionError("Target must be a living character")
        if target.team == attacker.team:
            raise InvalidActionError(
                "Target must be a living character on the opposing team"
            )

    def _update_outcome(self) -> None:
        if not self.living_enemies():
            self._outcome = BattleOutcome.VICTORY
        elif not self.living_players():
            self._outcome = BattleOutcome.DEFEAT

    def _advance_turn(self) -> None:
        """Move to the next living actor; start a new round when the order wraps."""
        self._turn_index += 1
        if self._turn_index >= len(self._turn_order):
            self._turn_index = 0
            self.round_number += 1
        self._skip_defeated_actors()

    def _skip_defeated_actors(self) -> None:
        """Advance past defeated characters until a living actor is found."""
        if self.is_over:
            return

        checked = 0
        while not self._turn_order[self._turn_index].is_alive:
            self._turn_index += 1
            if self._turn_index >= len(self._turn_order):
                self._turn_index = 0
                self.round_number += 1
            checked += 1
            if checked >= len(self._turn_order):
                # No living actors remain; outcome should already be set.
                self._update_outcome()
                return


def create_default_battle() -> Battle:
    """Create a battle using the example starting statistics from DESIGN.md."""
    players = [
        Character("Player 1", hp=30, attack=10, team=Team.PLAYER),
        Character("Player 2", hp=25, attack=12, team=Team.PLAYER),
        Character("Player 3", hp=35, attack=8, team=Team.PLAYER),
    ]
    enemies = [
        Character("Enemy 1", hp=25, attack=7, team=Team.ENEMY),
        Character("Enemy 2", hp=25, attack=7, team=Team.ENEMY),
    ]
    return Battle(players, enemies)
