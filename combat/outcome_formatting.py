"""Presentation labels for battle outcomes.

Formatting reads an outcome value and returns a string. It does not
change battle state or combat rules.
"""

from combat.battle import BattleOutcome


def format_battle_outcome(outcome: BattleOutcome) -> str:
    """Return the display label for one of the three battle outcomes."""
    labels = {
        BattleOutcome.ONGOING: "Ongoing",
        BattleOutcome.VICTORY: "Victory",
        BattleOutcome.DEFEAT: "Defeat",
    }
    return labels[outcome]
