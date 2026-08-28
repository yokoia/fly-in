"""Scenario Graph"""

from parsing import Passage, Scenario, Sector


class AirNetwork:
    """Graphing neighbors"""
    def __init__(self, scenario: Scenario) -> None:
        if scenario.start is None or scenario.end is None:
            raise ValueError("Map requires start and end hubs")
        self.sectors = scenario.sectors
        self.passages = scenario.passages
        self.start: str = scenario.start.name
        self.end: str = scenario.end.name
        self.neighbors: dict[str, list[str]] = {
            label: [] for label in scenario.sectors}

        for passage in scenario.passages:
            self.neighbors[passage.left_s].append(passage.right_s)
            self.neighbors[passage.right_s].append(passage.left_s)

    def reachable_neighbors(self, label: str) -> list[str]:
        return [ neighbor
            for neighbor in self.neighbors[label] if
            self.sectors[neighbor].meta_data['zone'] != "blocked"]

    def entry_cost(self, label: str) -> int:
        return ( 2
            if self.sectors[label].meta_data["zone"] == "restricted"
            else 1)

    def get_passage(self, a: str, b: str) -> Passage | None:
        for passage in self.passages:
            if {a, b} == {passage.left_s, passage.right_s}:
                return passage
        return None

