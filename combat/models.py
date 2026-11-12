"""Character and team models for the combat simulator."""

from enum import Enum


class Team(Enum):
    """Which side a character belongs to."""

    PLAYER = "player"
    ENEMY = "enemy"


class Character:
    """A combat participant with HP and a fixed attack value."""

    def __init__(self, name: str, hp: int, attack: int, team: Team) -> None:
        if attack < 0:
            raise ValueError("Attack cannot be negative")
        self.name = name
        self.hp = hp
        self.attack = attack
        self.team = team

    @property
    def is_alive(self) -> bool:
        """A character is defeated when HP reaches 0."""
        return self.hp > 0

    def __repr__(self) -> str:
        return (
            f"Character(name={self.name!r}, hp={self.hp}, "
            f"attack={self.attack}, team={self.team.value})"
        )
