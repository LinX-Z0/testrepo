"""Tests for presentation-only battle outcome labels."""

import unittest

from combat.battle import BattleOutcome
from combat.outcome_formatting import format_battle_outcome


class OutcomeFormatterTests(unittest.TestCase):
    def test_ongoing_returns_ongoing(self) -> None:
        self.assertEqual(format_battle_outcome(BattleOutcome.ONGOING), "Ongoing")

    def test_victory_returns_victory(self) -> None:
        self.assertEqual(format_battle_outcome(BattleOutcome.VICTORY), "Victory")

    def test_defeat_returns_defeat(self) -> None:
        self.assertEqual(format_battle_outcome(BattleOutcome.DEFEAT), "Defeat")


if __name__ == "__main__":
    unittest.main()
