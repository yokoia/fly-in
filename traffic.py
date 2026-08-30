"""Drone Simulation: let drones fly"""


from network import AirNetwork
from drone import Drone
from parsing import Scenario


ScheduledMove = tuple[Drone, bool, str]


class Traffic:
    """Simulation"""
    RESET = "\033[0m"
    PALETTE = {
        "black": 0, "blue": 21, "brown": 94, "crimson": 160,
        "cyan": 51, "darkred": 88, "gold": 220, "green": 46,
        "gray": 244, "grey": 244, "lime": 118, "magenta": 201,
        "maroon": 88, "orange": 208, "purple": 129, "red": 196,
        "violet": 177, "white": 15, "yellow": 226,
    }

    def __init__(self, scenario: Scenario, network: AirNetwork,
        drones: list[Drone]) -> None:
        self.scenario = scenario
        self.network = network
        self.drones = drones
        self.hub_occup: dict[str, int] = {
                label: 0 for label in scenario.sectors}
        self.passage_occup: dict[frozenset[str], int] = {
                frozenset((p.left_s, p.right_s)): 0
                for p in scenario.passages}
        self.hub_occup[network.start] = scenario.nb_drones

    def _reserve_next_hub(self, drone: Drone) -> ScheduledMove | None:
        """Reserve a connection and a hub"""
        target_label = drone.next_hub
        if target_label is None:
            return None

        if drone.crossing:
            return (drone, False, f"D{drone.number}-{target_label}")

        target = self.scenario.sectors[target_label]
        passage = self.network.get_passage(drone.location, target_label)
        if passage is None:
            return None
        zone_limit = target.meta_data["max_drones"]
        space = target.name == self.network.end
        if isinstance(zone_limit, int):
            space = space or self.hub_occup[target.name] < zone_limit
        key = frozenset((drone.location, target_label))
        if not space or self.passage_occup[key] >= passage.capacity:
            return None

        self.hub_occup[drone.location] -= 1
        self.hub_occup[target.name] += 1
        self.passage_occup[key] += 1
        restric = target.meta_data["zone"] == "restricted"
        shown_target = (f"{drone.location}-{target_label}"
                        if restric else target_label)
        return (drone, restric, f"D{drone.number}-{shown_target}")

    def turn(self) -> None:
        """moves that happen in a turn"""
        moves: list[ScheduledMove]= []
        for drone in sorted(
            self.drones, key=lambda drone: drone.position, reverse=True):
            reserved = self._reserve_next_hub(drone)
            if reserved is not None:
                moves.append(reserved)
        if not moves:
            raise RuntimeError("Simulation cannot make further progress")
        for drone, crosse, _ in moves:
            drone.crossing = crosse
            if crosse is False:
                drone.advance()
        self._display(moves)
        self.passage_occup = dict.fromkeys(self.passage_occup, 0)


    def play_turns(self) -> int:
        """start turns"""
        turns = 0
        while not all(drone.has_arrived for drone in self.drones):
            self.turn()
            turns += 1
        print(f"Total turns: {turns}")
        return turns

    @classmethod
    def _paint(cls, text: str, color: object) -> str:
        """coloring"""
        if not isinstance(color, str):
            return text
        colorr = color.lower()
        code = cls.PALETTE.get(colorr)
        if code is None:
            code = 16 + sum(map(ord, colorr)) % 216
        return f"\033[38;5;{code}m{text}{cls.RESET}"

    def _display(self, moves: list[ScheduledMove]) -> None:
        """print colored moves"""
        texts: list[str] = []
        for _, _, text in moves:
            target = text.rsplit("-", 1)[-1]
            target_color = self.network.sectors[target].meta_data["color"]
            texts.append(self._paint(text, target_color))
        print(" ".join(texts))
