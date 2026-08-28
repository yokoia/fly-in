"""Map file parsing for Fly-In scenarios."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class MapError(ValueError):
    """Raised when a scenario does not follow the Fly-In grammar."""


@dataclass
class Sector:
    """Hub"""
    name: str
    x: int
    y: int
    meta_data: dict[str, Any] = field(default_factory=
        lambda: {
            "color": None,
            "max_drones": 1,
            "zone": "normal",
        }
    )


@dataclass
class Passage:
    """Connection"""
    left_s: str
    right_s: str
    capacity: int = 1


@dataclass
class Scenario:
    """Scenario's data"""
    nb_drones: int = 0
    sectors: dict[str, Sector] = field(default_factory=dict)
    passages: list[Passage] = field(default_factory=list)
    start: Sector | None = None
    end: Sector | None = None


class MapParser:
    """Parsing Map"""

    DATA = {"nb_drones", "start_hub", "end_hub", "hub", "connection"}
    ZONES = {"normal", "priority", "restricted", "blocked"}

    def __init__(self) -> None:
        self.scen = Scenario()

    @staticmethod
    def load(source: str) -> list[str]:
        try:
            return Path(source).read_text(encoding="utf-8").splitlines()
        except OSError:
            raise MapError("Invalid file")

    def _nbdrones(self, nb: str) -> None:
        number = nb.split()
        if len(number) != 1:
            raise MapError("nb_drones must contain one number")
        if not number[0].isdigit():
            raise MapError("nb_drones must containes integers")
        amount = int(number[0])
        if amount <= 0:
            raise MapError("nb_drones must be greater than 0")
        self.scen.nb_drones = amount

    @staticmethod
    def _options(meta_data: list[str]) -> dict[str, Any]:
        if not meta_data:
            return {}
        data = " ".join(meta_data).strip()
        if not (data.startswith("[") and data.endswith("]")):
            raise MapError("Missing [ ]")
        result: dict[str, Any] = {}
        for item in data[1:-1].strip().split(): #["color=blue", "max_drones=1"]
            if "=" not in item:
                raise MapError("Invalid option: missing =")
            key, value = item.split("=", 1) #split only once = not multiple ===
            if not key or not value:
                raise MapError("Invalid option")
            if key in result:
                raise MapError(f"Duplicate option: {key}")
            result[key] = (int(value) if key != "color" and key != "zone"
                           and value.isdigit() else value)
        return result

    def _sector(self, data: str, payload: str) -> None:
        pieces = payload.split()
        if len(pieces) < 3:
            raise MapError(f"{data}: missing data")
        name = pieces[0]
        if "-" in name:
            raise MapError("zone names cannot contain dashes")
        try:
            x, y = int(pieces[1]), int(pieces[2])
        except ValueError:
            raise MapError(f"{data}: x and y must be integers")
        if name in self.scen.sectors:
            raise MapError(f"Duplicate zone name: {name}")

        metadata = self._options(pieces[3:])  # ["[color:red", "zone:...]"]
        for key in metadata:
            if key not in {"color", "zone", "max_drones"}:
                raise MapError(f"{data} does not allow option: {key}")
        if "zone" in metadata and metadata["zone"] not in self.ZONES:
            raise MapError(f"Invalid zone: {metadata['zone']}")
        if "max_drones" in metadata:
            maxd = metadata['max_drones']
            if not isinstance(maxd, int):
                raise MapError("max_drones must be integer")
            if maxd <= 0:
                raise MapError("max_drones must be > 0")

        sector = Sector(name, x, y)
        sector.meta_data.update(metadata)
        self.scen.sectors[name] = sector
        if data == "start_hub":
            if self.scen.start is not None:
                raise MapError("Multiple start_hub found")
            self.scen.start = sector
        if data == "end_hub":
            if self.scen.end is not None:
                raise MapError("Multiple end_hub found")
            self.scen.end = sector

    def _passage(self, payload: str) -> None:
        if not payload:
            raise MapError("connection: missing data")
        bracket = payload.find("[")
        conx = payload if bracket < 0 else payload[:bracket].strip()
        metadata = ( {} if bracket < 0 else
                self._options([payload[bracket:].strip()]))
        if "-" not in conx:
            raise MapError("connection format must be: a-b")
        left, right = (part.strip() for part in conx.split("-", 1))
        if left not in self.scen.sectors:
            raise MapError(f"{left} not in hubs")
        if right not in self.scen.sectors:
            raise MapError(f"{right} not in hubs")
        if left == right:
            raise MapError("connection: zone cannot connect to itself")
        if any({connection.left_s, connection.right_s} == {left, right}
                for connection in self.scen.passages):
            raise MapError(f"Duplicate connection: {left}-{right}")

        invalid = next((key for key in metadata if
                        key != "max_link_capacity"), None)  # only max_link is allowed for connections
        if invalid is not None:
            raise MapError(f"connection does not allow option: {invalid}")

        max_link = metadata.get("max_link_capacity", 1)
        if not isinstance(max_link, int):
            raise MapError("max_link_capacity must be an integer")
        if max_link <= 0:
            raise MapError("max_link_capacity must be > 0")
        self.scen.passages.append(Passage(left, right, max_link))
        
    def decode(self, lines: list[str]) -> Scenario:
        self.scen = Scenario()
        counting = 0
        hubs_order = True
        for number, raw_line in enumerate(lines, 1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            counting += 1
            if ":" not in line:
                raise MapError(f"Line {number}: missing ':'")
            command, payload = (part.strip() for part in line.split(":", 1))
            if command not in self.DATA:
                raise MapError(f"Line {number}: invalid keyword {command}")
            try:
                if counting == 1:
                    if command != "nb_drones":
                        raise MapError("first instruction must be 'nb_drones'")
                    self._nbdrones(payload)
                elif hubs_order and command in {"start_hub", "end_hub", "hub"}:
                    self._sector(command, payload)
                elif command == "connection":
                    self._passage(payload)
                    hubs_order = False
                elif command == "nb_drones":
                    raise MapError("nb_drones must be only one in the top")
                else:
                    raise MapError("all hubs must be above the connections")
            except MapError as e:
                raise MapError(f"Line {number}: {e}")
        if self.scen.nb_drones <= 0:
            raise MapError("Missing nb_drones")
        if self.scen.start is None:
            raise MapError("Missing start_hub")
        if self.scen.end is None:
            raise MapError("Missing end_hub")
        return self.scen
