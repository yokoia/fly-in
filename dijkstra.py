"""Planning drone routes using Dijkstra algorithm"""

from heapq import heappop, heappush
from network import AirNetwork


class RoutePlanner:
    """Dijkstra to find shortest paths"""
    def __init__(self, network: AirNetwork) -> None:
        self.network = network

    def shortest_route(self, connections: set[frozenset[str]]
        | None = None) -> list[str] | None:

        avoid_connections = connections or set()
        scores: dict[str, float] = {
            key: float("inf") for key in self.network.sectors}
        scores[self.network.start] = 0.0
        parents: dict[str, str] = {}
        heap = [(0.0, self.network.start)]

        while heap:
            score, hub = heappop(heap)
            if hub == self.network.end:
                break
            for neighbor in self.network.reachable_neighbors(hub):
                connection = frozenset((hub, neighbor))
                cost = float(self.network.entry_cost(neighbor))
                if connection in avoid_connections:
                    cost += len(self.network.sectors) + 1
                if (self.network.sectors[neighbor].meta_data["zone"]
                    == "priority"):
                    cost -= 0.1
                new_score = score + cost
                if new_score < scores[neighbor]:
                    scores[neighbor] = new_score
                    parents[neighbor] = hub
                    heappush(heap, (new_score, neighbor))
        if scores[self.network.end] == float("inf"):
            return None
        path = [self.network.end]
        while path[-1] != self.network.start:
            path.append(parents[path[-1]])
        return list(reversed(path))

    def find_multiple_routes(self, maximum: int) -> list[list[str]]:
        found_routes: list[list[str]] = []
        avoid_conn: set[frozenset[str]] = set()

        for _ in range(maximum):
            route = self.shortest_route(avoid_conn)
            if route is None or route in found_routes:
                break
            found_routes.append(route)
            for i in range(len(route) - 1):
                connection = frozenset((route[i], route[i + 1]))
                avoid_conn.add(connection)
        return found_routes
