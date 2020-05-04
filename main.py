import pyxel
import math  # math.floorを使うので必要
import time

import maze


class Map:
    SIZE = 8  # チップサイズ
    CHIP_WIDTH = 4  # 1列に5並んでいる
    CHIP_HEIGHT = 4  # 4行並でいる

    # マップチップ座標をスクリーン座標に変換
    @classmethod
    def to_screen(cls, i, j):
        return (i * cls.SIZE, j * cls.SIZE)

    # マップチップの描画
    @classmethod
    def draw_chip(cls, i, j, val):
        # スクリーン座標に変換
        x, y = cls.to_screen(i, j)
        # チップ画像の座標を計算
        u = (val % cls.CHIP_WIDTH) * cls.SIZE
        v = (math.floor(val / cls.CHIP_WIDTH)) * cls.SIZE
        pyxel.blt(x, y, 0, u, v, cls.SIZE, cls.SIZE, 2)

    def __init__(self):
        super().__init__()
        # マップデータ読み込み
        self.map = self.load_map("maze.txt")
        self.MAP_WIDTH = len(self.map[0])
        self.MAP_HEIGHT = len(self.map)
        print(self.MAP_WIDTH, self.MAP_HEIGHT)

    def load_map(self, txt):
        # マップ読み込み
        map = []
        map_file = open(txt)
        for line in map_file:
            # １行ずつ読み込み
            array = []
            data = line.split(",")
            for d in data:
                # 余分な文字を削除
                s = d.strip()
                if s == "":
                    break
                v = int(d.strip())
                array.append(v)
            map.append(array)

        return map

    def set_map(self, i, j, val):
        # 指定の位置に値を設定する
        self.map[j][i] = val

    def get_map(self):
        return self.map

    # マップから指定のチップを探す
    def search_map(self, val):
        # 指定の値が存在する座標を返す
        for j, arr in enumerate(self.map):
            for i, v in enumerate(arr):
                if v == val:
                    # 見つかった
                    return i, j
        raise ValueError(f"マップチップに val={val}がない")

    def is_wall(self, i, j):
        # 指定の座標が壁かどうかチェックする
        if i < 0 or self.MAP_WIDTH <= i:
            return True  # マップ外
        if j < 0 or self.MAP_HEIGHT <= j:
            return True  # マップ外

        v = self.map[j][i]
        if v in range(11, 16):
            # 壁なので移動できない
            return True

        # 移動可能
        return False


class App:
    MINI_MAP_SIZE = 4
    SIGHT = 2  # 視野
    ID = {"background": 0,
          "goal": 8,
          "wall": 11,
          "player": 15,
          }

    def __init__(self):
        pyxel.init(250, 200, fps=60)

        # mapを初期化
        self.map = Map()
        # 探索したか
        self.visited = [
            [False]*self.map.MAP_WIDTH for _ in range(self.map.MAP_HEIGHT)]

        # プレイヤーの位置を取得
        self.x, self.y = self.map.search_map(self.ID["player"])
        self.visit_around()

        # ゴールの位置を取得
        self.gx, self.gy = self.map.search_map(self.ID["goal"])
        # マップデータからプレイヤーを削除
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

        # マップの描画
        self.draw_map()
        # プレイヤーの描画
        # self.draw_player()

        left = 30 - int(time.time() - self.START_TIME)
        pyxel.text(5, H - 30, "ESCAPE HERE!!", pyxel.COLOR_YELLOW)
        pyxel.text(5, H - 10, f"TIMER: {left} second", pyxel.COLOR_YELLOW)

        if left <= 15:
            self.draw_mini_map()

    def input_key(self):
        # キー入力判定
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
            # 異動先が同じなので移動しない
            return False

        if self.map.is_wall(x_next, y_next):
            # 壁なので移動できない
            return False

        # 移動する
        self.map.set_map(self.x, self.y, self.ID["background"])
        self.map.set_map(x_next, y_next, self.ID["player"])

        self.x = x_next
        self.y = y_next

        return True

    # 周囲を訪れる
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

    # プレイヤーの描画
    def draw_player(self):
        Map.draw_chip(self.x, self.y, self.ID["player"])

    def draw_map(self):
        size = Map.SIZE
        W = self.map.MAP_WIDTH
        H = self.map.MAP_HEIGHT
        # 外枠の描画
        pyxel.rectb(0, 0, size*W, size*H, 5)

        # 各チップの描画
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
