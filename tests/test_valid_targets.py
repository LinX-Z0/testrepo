"""Independent contract tests for Battle.valid_targets."""

import unittest

from combat.battle import Battle, BattleOutcome, create_default_battle
from combat.combat import InvalidActionError
from combat.models import Character, Team


class ValidTargetsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.battle = create_default_battle()

    def state(self):
        """Capture values and identities, including order absent from snapshot()."""
        return (
            self.battle.snapshot(),
            self.battle.current_actor(),
            self.battle.is_over,
            tuple(self.battle.players),
            tuple(self.battle.enemies),
            tuple(self.battle._turn_order),
            self.battle._turn_index,
        )

    def assert_rejected(self, attacker: Character) -> None:
        before = self.state()
        attacker_hp = attacker.hp
        with self.assertRaises(InvalidActionError):
            self.battle.valid_targets(attacker)
        self.assertEqual(self.state(), before)
        self.assertEqual(attacker.hp, attacker_hp)

    def test_player_returns_living_enemies_in_roster_order(self) -> None:
        targets = self.battle.valid_targets(self.battle.players[0])
        self.assertEqual(targets, list(self.battle.enemies))
        self.assertIs(targets[0], self.battle.enemies[0])
        self.assertIs(targets[1], self.battle.enemies[1])

    def test_enemy_returns_living_players_in_roster_order(self) -> None:
        # Spread damage so Enemy 1 survives and becomes the current actor.
        self.battle.attack(self.battle.players[0], self.battle.enemies[0])
        self.battle.attack(self.battle.players[1], self.battle.enemies[1])
        self.battle.attack(self.battle.players[2], self.battle.enemies[0])
        self.assertIs(self.battle.current_actor(), self.battle.enemies[0])

        targets = self.battle.valid_targets(self.battle.enemies[0])
        self.assertEqual(targets, list(self.battle.players))
        self.assertIs(targets[0], self.battle.players[0])
        self.assertIs(targets[1], self.battle.players[1])
        self.assertIs(targets[2], self.battle.players[2])

    def test_defeated_opponents_are_excluded(self) -> None:
        self.battle.enemies[0].hp = 0
        targets = self.battle.valid_targets(self.battle.players[0])
        self.assertEqual(targets, [self.battle.enemies[1]])
        self.assertIs(targets[0], self.battle.enemies[1])

    def test_out_of_turn_attacker_is_rejected(self) -> None:
        self.assert_rejected(self.battle.players[1])

    def test_non_participant_with_duplicate_name_is_rejected(self) -> None:
        outsider = Character("Player 1", hp=30, attack=10, team=Team.PLAYER)
        self.assert_rejected(outsider)

    def test_rejected_after_victory(self) -> None:
        self.battle.players[0].attack = 25
        self.battle.players[1].attack = 25
        self.battle.attack(self.battle.players[0], self.battle.enemies[0])
        self.battle.attack(self.battle.players[1], self.battle.enemies[1])
        self.assertEqual(self.battle.outcome, BattleOutcome.VICTORY)
        self.assert_rejected(self.battle.players[0])
        self.assert_rejected(self.battle.enemies[0])

    def test_rejected_after_defeat(self) -> None:
        self.battle = Battle(
            [
                Character("Player 1", hp=7, attack=0, team=Team.PLAYER),
                Character("Player 2", hp=0, attack=0, team=Team.PLAYER),
                Character("Player 3", hp=0, attack=0, team=Team.PLAYER),
            ],
            [
                Character("Enemy 1", hp=25, attack=7, team=Team.ENEMY),
                Character("Enemy 2", hp=25, attack=7, team=Team.ENEMY),
            ],
        )
        self.battle.attack(self.battle.players[0], self.battle.enemies[0])
        self.battle.attack(self.battle.enemies[0], self.battle.players[0])
        self.assertEqual(self.battle.outcome, BattleOutcome.DEFEAT)
        self.assert_rejected(self.battle.enemies[0])
        self.assert_rejected(self.battle.players[0])

    def test_defeated_participant_rejected_while_battle_ongoing(self) -> None:
        self.battle = Battle(
            [
                Character("Player 1", hp=30, attack=0, team=Team.PLAYER),
                Character("Player 2", hp=7, attack=0, team=Team.PLAYER),
                Character("Player 3", hp=35, attack=0, team=Team.PLAYER),
            ],
            [
                Character("Enemy 1", hp=50, attack=7, team=Team.ENEMY),
                Character("Enemy 2", hp=50, attack=7, team=Team.ENEMY),
            ],
        )
        self.battle.attack(self.battle.players[0], self.battle.enemies[0])
        self.battle.attack(self.battle.players[1], self.battle.enemies[0])
        self.battle.attack(self.battle.players[2], self.battle.enemies[0])
        self.battle.attack(self.battle.enemies[0], self.battle.players[1])

        self.assertFalse(self.battle.players[1].is_alive)
        self.assertEqual(self.battle.outcome, BattleOutcome.ONGOING)
        self.assertIs(self.battle.current_actor(), self.battle.enemies[1])
        self.assert_rejected(self.battle.players[1])

    def test_enemy_excludes_defeated_players_preserving_roster_order(self) -> None:
        self.battle = Battle(
            [
                Character("Player 1", hp=30, attack=0, team=Team.PLAYER),
                Character("Player 2", hp=7, attack=0, team=Team.PLAYER),
                Character("Player 3", hp=35, attack=0, team=Team.PLAYER),
            ],
            [
                Character("Enemy 1", hp=50, attack=7, team=Team.ENEMY),
                Character("Enemy 2", hp=50, attack=7, team=Team.ENEMY),
            ],
        )
        self.battle.attack(self.battle.players[0], self.battle.enemies[0])
        self.battle.attack(self.battle.players[1], self.battle.enemies[0])
        self.battle.attack(self.battle.players[2], self.battle.enemies[0])
        self.battle.attack(self.battle.enemies[0], self.battle.players[1])

        self.assertFalse(self.battle.players[1].is_alive)
        self.assertIs(self.battle.current_actor(), self.battle.enemies[1])

        targets = self.battle.valid_targets(self.battle.enemies[1])
        self.assertEqual(
            targets,
            [self.battle.players[0], self.battle.players[2]],
        )
        self.assertIs(targets[0], self.battle.players[0])
        self.assertIs(targets[1], self.battle.players[2])

    def test_does_not_mutate_battle_state(self) -> None:
        before = self.state()
        self.battle.valid_targets(self.battle.players[0])
        self.assertEqual(self.state(), before)

    def test_repeated_calls_are_consistent_and_stateless(self) -> None:
        before = self.state()
        first = self.battle.valid_targets(self.battle.players[0])
        for _ in range(4):
            again = self.battle.valid_targets(self.battle.players[0])
            self.assertEqual(again, first)
            self.assertIs(again[0], first[0])
            self.assertIs(again[1], first[1])
            self.assertEqual(self.state(), before)

    def test_returns_new_list_without_copying_characters(self) -> None:
        first = self.battle.valid_targets(self.battle.players[0])
        second = self.battle.valid_targets(self.battle.players[0])

        self.assertIsNot(first, second)
        self.assertIsNot(first, self.battle.enemies)
        self.assertIs(first[0], self.battle.enemies[0])
        self.assertIs(first[1], self.battle.enemies[1])
        self.assertIs(second[0], self.battle.enemies[0])
        self.assertIs(second[1], self.battle.enemies[1])

        first.append(self.battle.players[0])
        self.assertEqual(len(self.battle.enemies), 2)
        self.assertEqual(
            self.battle.valid_targets(self.battle.players[0]),
            list(self.battle.enemies),
        )


if __name__ == "__main__":
    unittest.main()
