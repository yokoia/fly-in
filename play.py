"""Launching the program"""

import sys
from pathlib import Path

from network import AirNetwork
from drone import Drone
from parsing import MapError, MapParser
from dijkstra import RoutePlanner
from traffic import Traffic


class Play:
    """Launching the program using the method class.launch()"""
    @staticmethod
    def launch() -> None:
        args = sys.argv[1:]
        if len(args) != 1:
            print("Usage: make run <map_file>", file=sys.stderr)
            return
        file = args[0]
        if not Path(file).exists():
            print(f"Error: file not found: {file}", file=sys.stderr)
            return
        try:
            parser = MapParser()
            scenario = parser.decode(parser.load(file))
            network = AirNetwork(scenario)
            paths = RoutePlanner(network).find_multiple_routes(2)
            if not paths:
                raise ValueError("No path exists between start and end")
            drones = [Drone(number + 1, paths[number % len(paths)],
                    network.start) for number in range(scenario.nb_drones)]
            Traffic(scenario, network, drones).play_turns()
        except KeyboardInterrupt:
            print("\nSimulation interrupted.", file=sys.stderr)
            return
        except (MapError, RuntimeError, ValueError) as message:
            print("Error:", message, file=sys.stderr)


if __name__ == "__main__":
    Play.launch()
