"""Tests for Character and Team models."""

import unittest

from combat.models import Character, Team


class CharacterModelTests(unittest.TestCase):
    def test_character_stores_stats_and_team(self) -> None:
        fighter = Character("Player 1", hp=30, attack=10, team=Team.PLAYER)
        self.assertEqual(fighter.name, "Player 1")
        self.assertEqual(fighter.hp, 30)
        self.assertEqual(fighter.attack, 10)
        self.assertEqual(fighter.team, Team.PLAYER)

    def test_is_alive_when_hp_positive(self) -> None:
        fighter = Character("Player 1", hp=1, attack=5, team=Team.PLAYER)
        self.assertTrue(fighter.is_alive)

    def test_defeated_when_hp_reaches_zero(self) -> None:
        fighter = Character("Player 1", hp=0, attack=5, team=Team.PLAYER)
        self.assertFalse(fighter.is_alive)

    def test_defeated_when_hp_negative(self) -> None:
        # HP should not normally go negative, but is_alive uses HP > 0.
        fighter = Character("Player 1", hp=-1, attack=5, team=Team.PLAYER)
        self.assertFalse(fighter.is_alive)

    def test_negative_attack_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Character("Player 1", hp=10, attack=-1, team=Team.PLAYER)


if __name__ == "__main__":
    unittest.main()
