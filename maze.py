import random
import sys
from collections import deque

sys.setrecursionlimit(10**6)

HEIGHT, WIDTH = 19, 19
# 周りを通路にする
maze = [["0"]*WIDTH]
for _ in range(HEIGHT-2):
    m = ["0"] + ["11"]*(WIDTH - 2) + ["0"]
    maze.append(m)
maze.append(["0"]*WIDTH)
# print(*maze, sep="\n")

dx = [(1, 2), (-1, -2), (0, 0), (0, 0)]  # x軸のベクトル
dy = [(0, 0), (0, 0), (1, 2), (-1, -2)]  # y軸のベクトル


def make_maze(y, x):

    array = list(range(4))
    random.shuffle(array)  # ランダムに行く方向を決める

    for i in array:
        # 二つ先
        nx = x + dx[i][1]
        ny = y + dy[i][1]

        if ny < 1 or ny >= HEIGHT:  # 周りの壁を越えていたらスルー
            continue

        if nx < 1 or nx >= WIDTH:  # 周りの壁を越えていたらスルー
            continue

        if maze[ny][nx] == "0":  # 2つ先のマスがすでに開いていたらスルー
            continue

        for j in range(2):  # 通路を掘る
            ax = x + dx[i][j]
            ay = y + dy[i][j]
            maze[ay][ax] = "0"

        make_maze(ny, nx)  # 掘った先のところに移動


def main():
    sx = random.randint(1, WIDTH)
    sx = sx if sx % 2 == 1 else sx-1
    sy = 1
    maze[sy][sx] = "0"  # 初期地点
    make_maze(sy, sx)
    maze[sy][sx] = "15"  # スタートにプレイヤー

    # 壁を戻す
    for i in range(WIDTH):
        maze[0][i] = "11"
        maze[HEIGHT-1][i] = "11"
    for j in range(HEIGHT):
        maze[j][0] = "11"
        maze[j][-1] = "11"

    # 一番遠いところをゴールにする
    q = deque([(sy, sx)])
    max_dist = 0  # 最長距離
    gy, gx = 1, 1  # ゴール地点
    dx = [1, -1, 0, 0]
    dy = [0, 0, 1, -1]
    dist = [[-1]*WIDTH for _ in range(HEIGHT)]  # それぞれのマスの距離を持つ配列
    dist[sy][sx] = 0

    while q:  # キューに要素がなくなるまで回す

        y, x = q.popleft()  # 先頭から要素を取り出す

        for i in range(4):

            ny = y+dy[i]
            nx = x+dx[i]

            if ny <= 0 or nx <= 0 or ny+1 == HEIGHT or nx+1 == WIDTH:
                continue

            if maze[ny][nx] == "#":  # 次に行くマスが壁だったらスルー
                continue

            if dist[ny][nx] == -1:  # まだ通っていなかったら距離を更新
                q.append((ny, nx))
                dist[ny][nx] = dist[y][x]+1

                if max_dist < dist[ny][nx]:  # 最長距離を更新
                    gy, gx = ny, nx
                    max_dist = dist[ny][nx]

    maze[gy][gx] = "8"

    # for i in maze:
    #     print(*i)

    with open("maze.txt", "w") as f:
        for m in maze:
            row = ", ".join(m)
            row += "\n"
            f.write(row)


if __name__ == "__main__":
    main()
