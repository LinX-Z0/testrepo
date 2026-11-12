"""Low-level combat helpers: damage application and attack resolution."""

from combat.models import Character


class InvalidActionError(Exception):
    """Raised when an action is illegal and must not change combat state."""


def apply_damage(target: Character, damage: int) -> None:
    """Reduce target HP by damage, never below 0.

    Negative damage is rejected without changing state.
    """
    if damage < 0:
        raise InvalidActionError("Damage cannot be negative")
    target.hp = max(0, target.hp - damage)


def resolve_attack(attacker: Character, target: Character) -> None:
    """Apply the attacker's fixed attack damage to the target.

    Does not enforce turn order or targeting rules; Battle handles those.
    Rejects attacks from defeated characters without changing state.
    """
    if not attacker.is_alive:
        raise InvalidActionError("Defeated characters cannot attack")
    apply_damage(target, attacker.attack)
