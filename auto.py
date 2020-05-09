import math
import pyxel
import random
import sys
from collections import deque

sys.setrecursionlimit(10**6)


class Map:
    SIZE = 8         # size of each map chip
    CHIP_WIDTH = 4   # 4 map chips in a row
    CHIP_HEIGHT = 4  # 4 map chips in a column

    # in asset.pyxres, map-chips are aranged like:
    # [ 0][ 1][ 2][ 3]
    # [ 4][ 5][ 6][ 7]
    # [ 8][ 9][10][11]
    # [12][13][14][15]

    def __init__(self):
        self.map = [[12]*19 for _ in range(19)]
        self.MAP_WIDTH = len(self.map[0])
        self.MAP_HEIGHT = len(self.map)
        print(self.MAP_WIDTH, self.MAP_HEIGHT)

    # Convert map coordinates to screen coordinates
    @classmethod
    def to_screen(cls, i, j):
        return (i * cls.SIZE, j * cls.SIZE)

    # Drawing a map chip
    @classmethod
    def draw_chip(cls, i, j, val):
        # Convert to screen coordinates of the chip image
        x, y = cls.to_screen(i, j)
        u = (val % cls.CHIP_WIDTH) * cls.SIZE
        v = (math.floor(val / cls.CHIP_WIDTH)) * cls.SIZE
        pyxel.blt(x, y, 0, u, v, cls.SIZE, cls.SIZE, 2)

    def set_map(self, i, j, val):
        # Sets a value at a specified position.
        self.map[j][i] = val

    def get_map(self):
        return self.map

    # Find a specific chip on the map
    def search_map(self, val):
        # Returns the coordinates where the given value exists.
        for j, arr in enumerate(self.map):
            for i, v in enumerate(arr):
                # when found, return the coordinates
                if v == val:
                    return i, j
        raise ValueError(f"val={val} is not found in a map.")

    def is_wall(self, i, j):
        # Check if a given coordinate is a wall
        # outside the map
        if i < 0 or self.MAP_WIDTH <= i:
            return True
        if j < 0 or self.MAP_HEIGHT <= j:
            return True

        # wall
        v = self.map[j][i]
        if v in range(11, 16):
            return True

        # possible to move
        return False


class App:
    def __init__(self):
        # draw a screen with 'map'
        self.map = Map()
        self.HEIGHT = self.map.MAP_HEIGHT
        self.WIDTH = self.map.MAP_WIDTH

        # maze data is created at first
        # 'generateMaze()' initializes 'maze', 'log_of_dig', 'log_of_visit'
        self.maze = [["0"]*self.WIDTH]*self.HEIGHT
        self.log_of_dig = []
        self.log_of_visit = []
        self.generateMaze()

        # the cycle of "dig a maze and fill a path"
        self.CYCLE = len(self.log_of_dig)*2 + 1
        # Whether you explored the positon or not.
        self.visited = [
            [False]*self.map.MAP_WIDTH for _ in range(self.map.MAP_HEIGHT)]
        self.state = "dig"  # or "play"

        pyxel.init(152, 152, fps=10)
        pyxel.load("asset.pyxres")

        pyxel.cls(pyxel.COLOR_BLACK)
        pyxel.run(self.update, self.draw)

    def update(self):
        if self.state == "dig":
            f = pyxel.frame_count % self.CYCLE
            if f == 0:
                return
            i, j = self.log_of_dig[f-1]
            self.map.set_map(i, j, 0)  # delete player

            if f < len(self.log_of_dig):
                i, j = self.log_of_dig[f]
                self.map.set_map(i, j, 14)  # draw player
            else:  # f == len(self.log_of_dig)
                self.state = "play"

        elif self.state == "play":
            f = pyxel.frame_count % self.CYCLE - len(self.log_of_dig)
            i, j = self.log_of_visit[f-1]
            self.map.set_map(i, j, 12)  # delete player

            if f < len(self.log_of_visit):
                i, j = self.log_of_visit[f]
                self.map.set_map(i, j, 14)  # draw player
            elif f == len(self.log_of_visit):
                # regenerate maze & dig again
                self.generateMaze()
                self.state = "dig"

    def draw(self):
        self.draw_map()

    def draw_map(self):
        size = Map.SIZE
        W = self.map.MAP_WIDTH
        H = self.map.MAP_HEIGHT
        # Drawing the outer frame
        pyxel.rectb(0, 0, size*W, size*H, 5)

        # 各チップの描画
        for j, arr in enumerate(self.map.map):
            for i, d in enumerate(arr):
                Map.draw_chip(i, j, d)

    def make_maze(self, y, x):

        dx = [(1, 2), (-1, -2), (0, 0), (0, 0)]  # x-axis vector
        dy = [(0, 0), (0, 0), (1, 2), (-1, -2)]  # y-axis vector

        array = list(range(4))
        random.shuffle(array)  # Randomly decide on a preferred direction

        for i in array:
            # Two squares ahead
            nx = x + dx[i][1]
            ny = y + dy[i][1]

            if not(0 <= ny < self.HEIGHT) or not(0 <= nx < self.WIDTH):
                continue

            if self.maze[ny][nx] == "0":  # Two squares ahead of you are already open
                continue

            for j in range(2):  # dig a path
                ax = x + dx[i][j]
                ay = y + dy[i][j]
                if self.maze[ay][ax] == "12":
                    self.maze[ay][ax] = "0"
                    self.log_of_dig.append((ax, ay))

            self.make_maze(ny, nx)  # Move to the point where you dug.

    def get_random_start(self):
        sx = random.randint(1, self.WIDTH-1)
        # sx, sy must be odd
        sx = sx if sx % 2 == 1 else sx-1
        sy = 1
        return sx, sy

    def generateMaze(self):
        self.maze = [["0"]*self.WIDTH]
        # Make a pathway outline of the maze.
        #  "0": open
        # "12": wall
        self.maze = [["12"]*self.WIDTH for _ in range(self.HEIGHT)]

        self.log_of_dig = []  # a log of where to dig

        # make a maze
        sx, sy = self.get_random_start()
        self.log_of_dig.append((sx, sy))
        self.maze[sy][sx] = "0"

        self.make_maze(sy, sx)

        self.log_of_visit = self.log_of_dig[::-1]
        self.maze[sy][sx] = "14"  # player is at start


if __name__ == "__main__":
    App()
