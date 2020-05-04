import pyxel
import math
import time

import maze


class Map:
    SIZE = 8  # size of each map chip
    CHIP_WIDTH = 4  # 4 map chips in a row
    CHIP_HEIGHT = 4  # 4 map chips in a column

    # Convert map chip coordinates to screen coordinates
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

    def __init__(self):
        super().__init__()

        self.map = self.load_map("maze.txt")
        self.MAP_WIDTH = len(self.map[0])
        self.MAP_HEIGHT = len(self.map)
        print(self.MAP_WIDTH, self.MAP_HEIGHT)

    def load_map(self, txt):
        map = []
        map_file = open(txt)
        # Read a line at a time.
        for line in map_file:
            array = []
            data = line.split(",")
            for d in data:
                # Remove extra characters like \n
                s = d.strip()
                if s == "":
                    break
                v = int(d.strip())
                array.append(v)
            map.append(array)

        return map

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
    MINI_MAP_SIZE = 4
    SIGHT = 2  # how far player can see
    # You can see inside a circle with a radius of SIGHT
    ID = {"background": 0,
          "goal": 8,
          "wall": 11,
          "player": 15,
          }

    def __init__(self):
        pyxel.init(250, 200, fps=60)

        # initialize the map
        self.map = Map()
        # Whether you explored the positon or not.
        self.visited = [
            [False]*self.map.MAP_WIDTH for _ in range(self.map.MAP_HEIGHT)]

        # Get a player's position
        self.x, self.y = self.map.search_map(self.ID["player"])
        self.visit_around()

        # Get a goal's position
        self.gx, self.gy = self.map.search_map(self.ID["goal"])
        # Removing a player from the map data
        # self.map.set_map(self.x, self.y, 0)
        pyxel.load("asset.pyxres")
        self.START_TIME = time.time()
        pyxel.run(self.update, self.draw)

    def update(self):
        self.input_key()
        self.visit_around()

        left = 30 - int(time.time() - self.START_TIME)
        if left == 0:
            self.game_over()
        if self.x == self.gx and self.y == self.gy:
            self.game_clear()

    def draw(self):
        H = pyxel.height

        pyxel.cls(pyxel.COLOR_BLACK)

        self.draw_map()
        # プレイヤーの描画
        # self.draw_player()

        left = 30 - int(time.time() - self.START_TIME)
        pyxel.text(5, H - 30, "ESCAPE HERE!!", pyxel.COLOR_YELLOW)
        pyxel.text(5, H - 10, f"TIMER: {left} second", pyxel.COLOR_YELLOW)

        if left <= 15:
            self.draw_mini_map()

    def input_key(self):
        # judge key input
        x_next = self.x
        y_next = self.y
        if pyxel.btnp(pyxel.KEY_LEFT):
            x_next -= 1
        elif pyxel.btnp(pyxel.KEY_RIGHT):
            x_next += 1
        if pyxel.btnp(pyxel.KEY_UP):
            y_next -= 1
        elif pyxel.btnp(pyxel.KEY_DOWN):
            y_next += 1

        if self.x == x_next and self.y == y_next:
            # No need to move
            return False

        if self.map.is_wall(x_next, y_next):
            # player can't move above the wall.
            return False

        self.map.set_map(self.x, self.y, self.ID["background"])
        self.map.set_map(x_next, y_next, self.ID["player"])

        self.x = x_next
        self.y = y_next

        return True

    # visit around
    def visit_around(self):
        s = self.SIGHT
        W = self.map.MAP_WIDTH
        H = self.map.MAP_HEIGHT

        for dx in range(-s, s+1):
            for dy in range(-s, s+1):
                x = self.x + dx
                y = self.y + dy
                if not(0 <= x < W) or not(0 <= y < H):
                    continue
                if abs(dx) == abs(dy) == s:
                    continue
                self.visited[y][x] = True

    # draw player
    def draw_player(self):
        Map.draw_chip(self.x, self.y, self.ID["player"])

    def draw_map(self):
        size = Map.SIZE
        W = self.map.MAP_WIDTH
        H = self.map.MAP_HEIGHT
        # Drawing the outer frame
        pyxel.rectb(0, 0, size*W, size*H, 5)

        # Rendering of each map chip
        m = self.map.map
        s = self.SIGHT

        for dx in range(-s, s+1):
            for dy in range(-s, s+1):
                x = self.x + dx
                y = self.y + dy
                if not(0 <= x < W) or not(0 <= y < H):
                    continue
                if abs(dx) == abs(dy) == s:
                    continue
                Map.draw_chip(x, y, m[y][x])

    def draw_mini_map(self):
        W = pyxel.width
        size = self.MINI_MAP_SIZE

        for j, (arr, vj) in enumerate(zip(self.map.map, self.visited)):
            for i, (col, v) in enumerate(zip(arr[::-1], vj[::-1])):
                if not v:
                    continue
                x = W - (i+1) * size
                y = j * size
                pyxel.rect(x, y, size, size, col)
                pyxel.rectb(x, y, size, size, pyxel.COLOR_DARKGRAY)

    ### event ###
    def game_clear(self):
        H = pyxel.height
        pyxel.text(5, H - 20, "YOU WIN!!", pyxel.COLOR_YELLOW)
        pyxel.show()

    def game_over(self):
        H = pyxel.height
        pyxel.text(5, H - 20, "YOU Lose...", pyxel.COLOR_YELLOW)
        pyxel.show()


if __name__ == "__main__":
    maze.main()
    App()
