import random
from collections import deque

class Pathfinder:
    def __init__(self, tile_map, width, height):
        self.map = tile_map
        self.width = width
        self.height = height

    def walkable(self, x, y):
        return (
            0 <= x < self.width and
            0 <= y < self.height and
            self.map[y][x][1]['walkable']
        )

    def find_path(self, start, target=None):
        if target is None:
            return self._wander_step(start)

        return self._bfs_path(start, target)
    
    def _nearest_walkable_goal(self, gx, gy):
        best = None
        best_dist = float('inf')

        for dx in range(-1, 2):
            for dy in range(-1, 2):
                nx, ny = gx + dx, gy + dy

                if self.walkable(nx, ny):
                    dist = abs(dx) + abs(dy)
                    if dist < best_dist:
                        best = (nx, ny)
                        best_dist = dist

        return best


    def _wander_step(self, start):
        x, y = start

        directions = [
            (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (1, -1), (-1, 1), (-1, -1)
        ]

        random.shuffle(directions)
        chosen = random.choices(directions, k=random.randint(0, len(directions)))

        path = []
        for dx, dy in chosen:
            nx, ny = x + dx, y + dy
            if self.walkable(nx, ny) and nx < self.width and ny < self.height:
                path.append((dx, dy))

        path.reverse()
        return path

    def _bfs_path(self, start, goal):
        sx, sy = start
        gx, gy = goal

        if not self.walkable(sx, sy):
            return []

        if not self.walkable(gx, gy):
            adjusted = self._nearest_walkable_goal(gx, gy)
            if adjusted is None:
                return []
            gx, gy = adjusted

        if (sx, sy) == (gx, gy):
            return []

        from collections import deque
        queue = deque([(sx, sy)])
        came_from = {(sx, sy): None}

        directions = [(1,0), (-1,0), (0,1), (0,-1)]

        while queue:
            x, y = queue.popleft()

            if (x, y) == (gx, gy):
                break

            for dx, dy in directions:
                nx, ny = x + dx, y + dy

                if (nx, ny) not in came_from and self.walkable(nx, ny):
                    came_from[(nx, ny)] = (x, y)
                    queue.append((nx, ny))

        if (gx, gy) not in came_from:
            return []

        path = []
        current = (gx, gy)

        while current != (sx, sy):
            prev = came_from[current]
            if prev is None:
                return []

            path.append((current[0] - prev[0], current[1] - prev[1]))
            current = prev

        path.reverse()
        return path

