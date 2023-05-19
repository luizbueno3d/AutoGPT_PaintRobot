import numpy as np
from heapq import heappush, heappop
from typing import Callable, Dict, List, Set, Tuple

class PaintOptimization:
    def __init__(self, heuristic_function: Callable = None):
        if heuristic_function is None:
            self.heuristic = self._manhattan_distance
        else:
            self.heuristic = heuristic_function

    def _manhattan_distance(self, a: Tuple[int, int], b: Tuple[int, int]) -> int:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def _a_star_search(self, building_edges: Set[Tuple[int, int]], start: Tuple[int, int], end: Tuple[int, int]) -> Tuple[Dict[Tuple[int, int], Tuple[int, int]], Dict[Tuple[int, int], int]]:
        frontier = []
        heappush(frontier, (0, start))
        came_from = dict()
        cost_so_far = dict()
        came_from[start] = None
        cost_so_far[start] = 0

        while frontier:
            _, current = heappop(frontier)

            if current == end:
                break

            for next in self._neighbors(current, building_edges):
                new_cost = cost_so_far[current] + 1
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.heuristic(end, next)
                    heappush(frontier, (priority, next))
                    came_from[next] = current

        return came_from, cost_so_far

    def _neighbors(self, pos: Tuple[int, int], building_edges: Set[Tuple[int, int]]) -> List[Tuple[int, int]]:
        neighbors = [
            (pos[0] + 1, pos[1]),
            (pos[0] - 1, pos[1]),
            (pos[0], pos[1] + 1),
            (pos[0], pos[1] - 1),
        ]
        valid_neighbors = [n for n in neighbors if n not in building_edges]
        return valid_neighbors

    def _reconstruct_path(self, came_from: Dict[Tuple[int, int], Tuple[int, int]], start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
        path = [end]
        while path[-1] != start:
            path.append(came_from[path[-1]])
        path.reverse()
        return path

    def find_closest_area(self, current_position: Tuple[int, int], painting_areas: List[Tuple[Tuple[int, int], Tuple[int, int]]]) -> Tuple[Tuple[Tuple[int, int], Tuple[int, int]], int]:
        min_distance = float('inf')
        closest_area = None
        closest_index = -1

        for index, area in enumerate(painting_areas):
            distance = np.linalg.norm(np.array(current_position) - np.array(area[0]))
            if distance < min_distance:
                min_distance = distance
                closest_area = area
                closest_index = index

        return closest_area, closest_index

    def _optimize_painting(self, building_edges: Set[Tuple[int, int]], painting_areas: List[Tuple[Tuple[int, int], Tuple[int, int]]]) -> List[Tuple[str, int, int, int]]:
        optimized_painting_commands = []
        current_position = (0, 0)

        while painting_areas:
            closest_area, closest_index = self.find_closest_area(current_position, painting_areas)
            start, end = closest_area

            came_from, _ = self._a_star_search(building_edges, start, end)
            path = self._reconstruct_path(came_from, start, end)

            for pos in path:
                optimized_painting_commands.append(('G1', pos[0], pos[1], 3000))  # Adjust the speed as needed

            painting_areas.pop(closest_index)
            current_position = end

        return optimized_painting_commands

if __name__ == "__main__":
    paint_optimizer = PaintOptimization()

    # Example input, replace with actual data
    building_edges = {(2, 2), (2, 3), (2, 4), (2, 5)}
    painting_areas = [((1, 1), (4, 1)), ((4, 4), (1, 4))]

    optimized_painting_commands = paint_optimizer._optimize_painting(building_edges, painting_areas)
    print(optimized_painting_commands)
