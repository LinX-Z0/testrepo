"""Independent contract tests for Battle.preview_attack."""

import unittest

from combat.battle import Battle, BattleOutcome, create_default_battle
from combat.combat import InvalidActionError
from combat.models import Character, Team


class AttackPreviewTests(unittest.TestCase):
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

    def assert_rejected(self, attacker, target) -> None:
        before = self.state()
        outsider_hp = (attacker.hp, target.hp)
        with self.assertRaises(InvalidActionError):
            self.battle.preview_attack(attacker, target)
        self.assertEqual(self.state(), before)
        self.assertEqual((attacker.hp, target.hp), outsider_hp)

    def assert_prediction(self, damage, hp_after, would_defeat) -> None:
        before = self.state()
        result = self.battle.preview_attack(
            self.battle.current_actor(), self.battle.enemies[0]
        )
        self.assertIsInstance(result, dict)
        self.assertEqual(result, {
            "damage": damage,
            "target_hp_after": hp_after,
            "would_defeat": would_defeat,
        })
        self.assertIs(result["would_defeat"], would_defeat)
        self.assertEqual(self.state(), before)

    def test_nonlethal_prediction_has_exact_contract_and_preserves_state(self):
        self.assert_prediction(10, 15, False)

    def test_exact_lethal_prediction_preserves_state(self):
        self.battle.enemies[0].hp = 10
        self.assert_prediction(10, 0, True)

    def test_overkill_reports_full_damage_and_clamps_hp(self):
        self.battle.enemies[0].hp = 3
        self.assert_prediction(10, 0, True)

    def test_zero_damage_is_valid_and_does_not_defeat_living_target(self):
        self.battle.players[0].attack = 0
        self.assert_prediction(0, 25, False)

    def test_out_of_turn_attacker_is_rejected(self):
        self.assert_rejected(self.battle.players[1], self.battle.enemies[0])

    def test_outsider_attacker_with_identical_stats_is_rejected(self):
        outsider = Character("Player 1", hp=30, attack=10, team=Team.PLAYER)
        self.assert_rejected(outsider, self.battle.enemies[0])

    def test_defeated_attacker_is_rejected(self):
        self.battle = Battle(
            [Character("P1", 0, 10, Team.PLAYER),
             Character("P2", 25, 12, Team.PLAYER),
             Character("P3", 35, 8, Team.PLAYER)],
            [Character("E1", 25, 7, Team.ENEMY),
             Character("E2", 25, 7, Team.ENEMY)],
        )
        self.assert_rejected(self.battle.players[0], self.battle.enemies[0])

    def test_ally_target_is_rejected(self):
        self.assert_rejected(self.battle.players[0], self.battle.players[1])

    def test_self_target_is_rejected(self):
        self.assert_rejected(self.battle.players[0], self.battle.players[0])

    def test_defeated_opponent_target_is_rejected(self):
        self.battle.enemies[0].hp = 0
        self.assert_rejected(self.battle.players[0], self.battle.enemies[0])

    def test_outsider_target_with_identical_stats_is_rejected(self):
        outsider = Character("Enemy 1", hp=25, attack=7, team=Team.ENEMY)
        self.assert_rejected(self.battle.players[0], outsider)

    def test_repeated_previews_preserve_state_and_result(self):
        before = self.state()
        for _ in range(5):
            result = self.battle.preview_attack(
                self.battle.players[0], self.battle.enemies[0]
            )
            self.assertEqual(result, {
                "damage": 10, "target_hp_after": 15, "would_defeat": False,
            })
            self.assertEqual(self.state(), before)

    def test_preview_then_attack_matches_prediction(self):
        for hp in (25, 10, 3):
            with self.subTest(target_hp=hp):
                self.battle = create_default_battle()
                attacker, target = self.battle.players[0], self.battle.enemies[0]
                target.hp = hp
                result = self.battle.preview_attack(attacker, target)
                self.battle.attack(attacker, target)
                self.assertEqual(target.hp, result["target_hp_after"])
                self.assertIs(not target.is_alive, result["would_defeat"])
                self.assertIs(self.battle.current_actor(), self.battle.players[1])

    def test_previews_preserve_turn_sequence_and_round_wrap(self):
        actors = self.battle.players + self.battle.enemies
        targets = [self.battle.enemies[0], self.battle.enemies[1],
                   self.battle.enemies[0], self.battle.players[0],
                   self.battle.players[1]]
        for actor, target in zip(actors, targets):
            self.assertIs(self.battle.current_actor(), actor)
            before = self.state()
            prediction = self.battle.preview_attack(actor, target)
            self.assertEqual(prediction, {
                "damage": actor.attack,
                "target_hp_after": target.hp - actor.attack,
                "would_defeat": False,
            })
            self.assertEqual(self.state(), before)
            self.battle.attack(actor, target)
        self.assertEqual(self.battle.round_number, 2)
        self.assertIs(self.battle.current_actor(), self.battle.players[0])
        self.assert_prediction(10, 0, True)

    def test_preview_of_final_blow_does_not_end_battle(self):
        self.battle.players[0].attack = 25
        self.battle.attack(self.battle.players[0], self.battle.enemies[0])
        self.battle.players[1].attack = 25
        before = self.state()
        result = self.battle.preview_attack(
            self.battle.players[1], self.battle.enemies[1]
        )
        self.assertEqual(result, {
            "damage": 25, "target_hp_after": 0, "would_defeat": True,
        })
        self.assertEqual(self.state(), before)
        self.assertEqual(self.battle.outcome, BattleOutcome.ONGOING)

    def test_preview_rejected_after_victory(self):
        self.battle.players[0].attack = 25
        self.battle.players[1].attack = 25
        self.battle.attack(self.battle.players[0], self.battle.enemies[0])
        self.battle.attack(self.battle.players[1], self.battle.enemies[1])
        self.assertEqual(self.battle.outcome, BattleOutcome.VICTORY)
        self.assert_rejected(self.battle.enemies[0], self.battle.players[2])

    def test_preview_rejected_after_defeat(self):
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
        self.assert_rejected(self.battle.enemies[1], self.battle.players[0])


if __name__ == "__main__":
    unittest.main()
