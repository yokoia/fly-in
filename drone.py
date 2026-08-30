"""Drone scenario planning"""

from dataclasses import dataclass


@dataclass
class Drone:
    """Drone info"""
    number: int
    route: list[str]
    location: str
    position: int = 0
    crossing: bool = False

    @property
    def next_hub(self) -> str | None:
        i = self.position + 1
        if i != len(self.route):
            return self.route[i]
        return None

    @property
    def has_arrived(self) -> bool:
        return self.position == len(self.route) - 1

    def advance(self) -> None:
        """moving the drone"""
        self.position += 1
        self.location = self.route[self.position]