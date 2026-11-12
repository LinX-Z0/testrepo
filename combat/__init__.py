"""Turn-based combat simulator package."""

from combat.battle import Battle, BattleOutcome, create_default_battle
from combat.combat import InvalidActionError, apply_damage, resolve_attack
from combat.models import Character, Team

__all__ = [
    "Battle",
    "BattleOutcome",
    "Character",
    "InvalidActionError",
    "Team",
    "apply_damage",
    "create_default_battle",
    "resolve_attack",
]
