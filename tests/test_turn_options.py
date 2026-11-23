"""Independent contract tests for Battle.turn_options."""

import unittest
from unittest.mock import patch

from combat.battle import Battle, BattleOutcome, create_default_battle
from combat.combat import InvalidActionError
from combat.models import Character, Team


class TurnOptionsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.battle = create_default_battle()

    def state(self):
        """Capture character values and battle identities, order, and counters."""
        return (
            self.battle.snapshot(),
            self.battle.current_actor(),
            self.battle.is_over,
            tuple(self.battle.players),
            tuple(self.battle.enemies),
            tuple(self.battle._participants),
            tuple(self.battle._turn_order),
            self.battle._turn_index,
            tuple(c.team for c in self.battle._participants),
        )

    def assert_rejected(self, attacker: Character) -> None:
        before = self.state()
        attacker_before = vars(attacker).copy()
        with self.assertRaises(InvalidActionError):
            self.battle.turn_options(attacker)
        self.assertEqual(self.state(), before)
        self.assertEqual(vars(attacker), attacker_before)

    def advance_to_enemy(self) -> None:
        self.battle.attack(self.battle.players[0], self.battle.enemies[0])
        self.battle.attack(self.battle.players[1], self.battle.enemies[1])
        self.battle.attack(self.battle.players[2], self.battle.enemies[0])
        self.assertIs(self.battle.current_actor(), self.battle.enemies[0])

    def assert_options(self, actor, targets, predictions) -> None:
        before = self.state()
        options = self.battle.turn_options(actor)
        self.assertIsInstance(options, list)
        self.assertEqual(len(options), len(targets))
        for option, target, prediction in zip(options, targets, predictions):
            self.assertIsInstance(option, dict)
            self.assertEqual(
                set(option),
                {"target", "damage", "target_hp_after", "would_defeat"},
            )
            self.assertIsInstance(option["target"], Character)
            self.assertIs(option["target"], target)
            self.assertIs(type(option["damage"]), int)
            self.assertIs(type(option["target_hp_after"]), int)
            self.assertIs(type(option["would_defeat"]), bool)
            self.assertEqual(
                (option["damage"], option["target_hp_after"], option["would_defeat"]),
                prediction,
            )
        self.assertEqual(self.state(), before)

    def test_player_options_have_exact_schema_predictions_and_target_identity(self) -> None:
        self.assert_options(
            self.battle.players[0], self.battle.enemies,
            [(10, 15, False), (10, 15, False)],
        )

    def test_enemy_options_preserve_player_roster_order(self) -> None:
        self.advance_to_enemy()
        self.assert_options(
            self.battle.enemies[0], self.battle.players,
            [(7, 23, False), (7, 18, False), (7, 28, False)],
        )

    def test_exact_lethal_and_overkill_predictions(self) -> None:
        self.battle = Battle(
            [Character("P1", 30, 10, Team.PLAYER),
             Character("P2", 25, 12, Team.PLAYER),
             Character("P3", 35, 8, Team.PLAYER)],
            [Character("E1", 10, 7, Team.ENEMY),
             Character("E2", 3, 7, Team.ENEMY)],
        )
        self.assert_options(
            self.battle.players[0], self.battle.enemies,
            [(10, 0, True), (10, 0, True)],
        )

    def test_zero_attack_predictions(self) -> None:
        self.battle = Battle(
            [Character("P1", 30, 0, Team.PLAYER),
             Character("P2", 25, 12, Team.PLAYER),
             Character("P3", 35, 8, Team.PLAYER)],
            [Character("E1", 25, 7, Team.ENEMY),
             Character("E2", 13, 7, Team.ENEMY)],
        )
        self.assert_options(
            self.battle.players[0], self.battle.enemies,
            [(0, 25, False), (0, 13, False)],
        )

    def test_player_excludes_enemy_defeated_by_normal_attacks(self) -> None:
        self.battle.attack(self.battle.players[0], self.battle.enemies[0])
        self.battle.attack(self.battle.players[1], self.battle.enemies[0])
        self.battle.attack(self.battle.players[2], self.battle.enemies[0])
        self.battle.attack(self.battle.enemies[1], self.battle.players[0])
        self.assertEqual(self.battle.round_number, 2)
        self.assertFalse(self.battle.enemies[0].is_alive)
        self.assert_options(
            self.battle.players[0], [self.battle.enemies[1]], [(10, 15, False)],
        )

    def test_enemy_excludes_defeated_middle_player_preserving_order(self) -> None:
        self.battle = Battle(
            [Character("P1", 30, 0, Team.PLAYER),
             Character("P2", 7, 0, Team.PLAYER),
             Character("P3", 35, 0, Team.PLAYER)],
            [Character("E1", 25, 7, Team.ENEMY),
             Character("E2", 25, 7, Team.ENEMY)],
        )
        self.advance_to_enemy()
        self.battle.attack(self.battle.enemies[0], self.battle.players[1])
        self.assertFalse(self.battle.players[1].is_alive)
        self.assert_options(
            self.battle.enemies[1], [self.battle.players[0], self.battle.players[2]],
            [(7, 23, False), (7, 28, False)],
        )

    def test_duplicate_target_names_preserve_distinct_roster_identities(self) -> None:
        self.battle = Battle(
            [Character("P1", 30, 10, Team.PLAYER),
             Character("P2", 25, 12, Team.PLAYER),
             Character("P3", 35, 8, Team.PLAYER)],
            [Character("Same", 25, 7, Team.ENEMY),
             Character("Same", 13, 7, Team.ENEMY)],
        )
        self.assert_options(
            self.battle.players[0], self.battle.enemies,
            [(10, 15, False), (10, 3, False)],
        )

    def test_options_match_valid_targets_and_preview_through_full_round(self) -> None:
        actors = self.battle.players + self.battle.enemies
        targets = [self.battle.enemies[0], self.battle.enemies[1],
                   self.battle.enemies[0], self.battle.players[0],
                   self.battle.players[1]]
        for actor, attack_target in zip(actors, targets):
            with self.subTest(actor=actor.name):
                before = self.state()
                legal_targets = self.battle.valid_targets(actor)
                expected = [self.battle.preview_attack(actor, t) for t in legal_targets]
                options = self.battle.turn_options(actor)
                self.assertEqual(len(options), len(legal_targets))
                for option, target, preview in zip(options, legal_targets, expected):
                    self.assertIs(option["target"], target)
                    self.assertEqual(option, dict(preview, target=target))
                self.assertEqual(self.state(), before)
            self.battle.attack(actor, attack_target)

    def test_predicted_final_blow_does_not_end_battle(self) -> None:
        self.battle = Battle(
            [Character("P1", 30, 25, Team.PLAYER),
             Character("P2", 25, 25, Team.PLAYER),
             Character("P3", 35, 8, Team.PLAYER)],
            [Character("E1", 25, 7, Team.ENEMY),
             Character("E2", 25, 7, Team.ENEMY)],
        )
        self.battle.attack(self.battle.players[0], self.battle.enemies[0])
        self.assert_options(
            self.battle.players[1], [self.battle.enemies[1]], [(25, 0, True)],
        )
        self.assertEqual(self.battle.outcome, BattleOutcome.ONGOING)
        self.battle.attack(self.battle.players[1], self.battle.enemies[1])
        self.assertEqual(self.battle.outcome, BattleOutcome.VICTORY)

    def test_turn_options_returns_empty_when_valid_targets_returns_empty(self) -> None:
        actor = self.battle.current_actor()
        before = self.state()
        with patch.object(self.battle, "valid_targets", return_value=[]), \
             patch.object(self.battle, "preview_attack") as mock_preview:
            options = self.battle.turn_options(actor)
        self.assertEqual(options, [])
        mock_preview.assert_not_called()
        self.assertEqual(self.state(), before)

    def test_out_of_turn_player_is_rejected(self) -> None:
        self.assert_rejected(self.battle.players[1])

    def test_out_of_turn_enemy_is_rejected(self) -> None:
        self.assert_rejected(self.battle.enemies[0])

    def test_previous_actor_is_rejected(self) -> None:
        self.battle.attack(self.battle.players[0], self.battle.enemies[0])
        self.assert_rejected(self.battle.players[0])

    def test_non_participant_is_rejected(self) -> None:
        self.assert_rejected(Character("Outsider", 50, 1, Team.PLAYER))

    def test_duplicate_name_player_outsider_is_rejected(self) -> None:
        self.assert_rejected(Character("Player 1", 30, 10, Team.PLAYER))

    def test_duplicate_name_enemy_outsider_is_rejected(self) -> None:
        self.advance_to_enemy()
        enemy = self.battle.enemies[0]
        self.assert_rejected(Character(enemy.name, enemy.hp, enemy.attack, enemy.team))

    def test_defeated_participant_is_rejected(self) -> None:
        self.battle = Battle(
            [Character("P1", 30, 0, Team.PLAYER),
             Character("P2", 0, 0, Team.PLAYER),
             Character("P3", 30, 0, Team.PLAYER)],
            [Character("E1", 25, 7, Team.ENEMY),
             Character("E2", 25, 7, Team.ENEMY)],
        )
        self.assertEqual(self.battle.outcome, BattleOutcome.ONGOING)
        self.assert_rejected(self.battle.players[1])

    def test_calls_after_victory_are_rejected(self) -> None:
        self.battle = Battle(
            [Character("P1", 30, 25, Team.PLAYER),
             Character("P2", 30, 25, Team.PLAYER),
             Character("P3", 30, 8, Team.PLAYER)],
            [Character("E1", 25, 7, Team.ENEMY),
             Character("E2", 25, 7, Team.ENEMY)],
        )
        self.battle.attack(self.battle.players[0], self.battle.enemies[0])
        self.battle.attack(self.battle.players[1], self.battle.enemies[1])
        self.assertEqual(self.battle.outcome, BattleOutcome.VICTORY)
        for attacker in self.battle.players + self.battle.enemies:
            with self.subTest(attacker=attacker.name):
                self.assert_rejected(attacker)

    def test_calls_after_defeat_are_rejected(self) -> None:
        self.battle = Battle(
            [Character("P1", 7, 0, Team.PLAYER),
             Character("P2", 0, 0, Team.PLAYER),
             Character("P3", 0, 0, Team.PLAYER)],
            [Character("E1", 25, 7, Team.ENEMY),
             Character("E2", 25, 7, Team.ENEMY)],
        )
        self.battle.attack(self.battle.players[0], self.battle.enemies[0])
        self.battle.attack(self.battle.enemies[0], self.battle.players[0])
        self.assertEqual(self.battle.outcome, BattleOutcome.DEFEAT)
        for attacker in self.battle.players + self.battle.enemies:
            with self.subTest(attacker=attacker.name):
                self.assert_rejected(attacker)

    def test_queries_preserve_state_and_turn_sequence_across_round(self) -> None:
        actors = self.battle.players + self.battle.enemies
        targets = [self.battle.enemies[0], self.battle.enemies[1],
                   self.battle.enemies[0], self.battle.players[0],
                   self.battle.players[1]]
        for actor, target in zip(actors, targets):
            self.assertIs(self.battle.current_actor(), actor)
            before = self.state()
            self.battle.turn_options(actor)
            self.assertEqual(self.state(), before)
            self.battle.attack(actor, target)
        self.assertEqual(self.battle.round_number, 2)
        self.assertIs(self.battle.current_actor(), self.battle.players[0])

    def test_repeated_calls_return_independent_lists_and_dictionaries(self) -> None:
        actor = self.battle.players[0]
        before = self.state()
        first = self.battle.turn_options(actor)
        second = self.battle.turn_options(actor)
        self.assertIsInstance(first, list)
        self.assertEqual(len(first), 2)
        self.assertEqual(first, second)
        self.assertIsNot(first, second)
        self.assertIsNot(first[0], first[1])
        for left, right in zip(first, second):
            self.assertIsInstance(left, dict)
            self.assertIsNot(left, right)

        first[0].clear()
        first[1]["extra"] = "caller-owned change"
        first.clear()
        for _ in range(3):
            again = self.battle.turn_options(actor)
            self.assertEqual(again, second)
            self.assertIsNot(again, second)
            for left, right in zip(again, second):
                self.assertIsNot(left, right)
            self.assertEqual(self.state(), before)


if __name__ == "__main__":
    unittest.main()
