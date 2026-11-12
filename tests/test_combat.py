"""Tests for low-level damage and attack helpers."""

import unittest

from combat.combat import InvalidActionError, apply_damage, resolve_attack
from combat.models import Character, Team


class ApplyDamageTests(unittest.TestCase):
    def test_apply_damage_reduces_hp(self) -> None:
        target = Character("Enemy 1", hp=25, attack=7, team=Team.ENEMY)
        apply_damage(target, 10)
        self.assertEqual(target.hp, 15)

    def test_hp_cannot_fall_below_zero(self) -> None:
        target = Character("Enemy 1", hp=5, attack=7, team=Team.ENEMY)
        apply_damage(target, 10)
        self.assertEqual(target.hp, 0)
        self.assertFalse(target.is_alive)

    def test_negative_damage_rejected_without_state_change(self) -> None:
        target = Character("Enemy 1", hp=25, attack=7, team=Team.ENEMY)
        with self.assertRaises(InvalidActionError):
            apply_damage(target, -1)
        self.assertEqual(target.hp, 25)


class ResolveAttackTests(unittest.TestCase):
    def test_attack_deals_attacker_attack_stat(self) -> None:
        attacker = Character("Player 1", hp=30, attack=10, team=Team.PLAYER)
        target = Character("Enemy 1", hp=25, attack=7, team=Team.ENEMY)
        resolve_attack(attacker, target)
        self.assertEqual(target.hp, 15)
        self.assertEqual(attacker.hp, 30)

    def test_defeated_attacker_rejected_without_state_change(self) -> None:
        attacker = Character("Player 1", hp=0, attack=10, team=Team.PLAYER)
        target = Character("Enemy 1", hp=25, attack=7, team=Team.ENEMY)
        with self.assertRaises(InvalidActionError):
            resolve_attack(attacker, target)
        self.assertEqual(target.hp, 25)

    def test_zero_attack_deals_no_damage(self) -> None:
        attacker = Character("Player 1", hp=30, attack=0, team=Team.PLAYER)
        target = Character("Enemy 1", hp=25, attack=7, team=Team.ENEMY)
        resolve_attack(attacker, target)
        self.assertEqual(target.hp, 25)


if __name__ == "__main__":
    unittest.main()
