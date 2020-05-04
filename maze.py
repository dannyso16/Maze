import random
import sys
from collections import deque

sys.setrecursionlimit(10**6)

HEIGHT, WIDTH = 19, 19
# Make a pathway around it.
maze = [["0"]*WIDTH]
for _ in range(HEIGHT-2):
    m = ["0"] + ["11"]*(WIDTH - 2) + ["0"]
    maze.append(m)
maze.append(["0"]*WIDTH)
# print(*maze, sep="\n")

dx = [(1, 2), (-1, -2), (0, 0), (0, 0)]  # x-axis vector
dy = [(0, 0), (0, 0), (1, 2), (-1, -2)]  # y-axis vector


def make_maze(y, x):

    array = list(range(4))
    random.shuffle(array)  # Randomly decide on a preferred direction

    for i in array:
        # 二つ先
        nx = x + dx[i][1]
        ny = y + dy[i][1]

        if ny < 1 or ny >= HEIGHT:  # outside the map
            continue

        if nx < 1 or nx >= WIDTH:  # outside the map
            continue

        if maze[ny][nx] == "0":  # Two squares ahead of you are already open
            continue

        for j in range(2):  # dig a path
            ax = x + dx[i][j]
            ay = y + dy[i][j]
            maze[ay][ax] = "0"

        make_maze(ny, nx)  # Move to the point where you dug.


def main():
    # start
    sx = random.randint(1, WIDTH)
    sx = sx if sx % 2 == 1 else sx-1
    sy = 1
    maze[sy][sx] = "0"
    make_maze(sy, sx)
    maze[sy][sx] = "15"  # player is at start

    # Put the perimeter back on the wall.
    for i in range(WIDTH):
        maze[0][i] = "11"
        maze[HEIGHT-1][i] = "11"
    for j in range(HEIGHT):
        maze[j][0] = "11"
        maze[j][-1] = "11"

    # I'll take the farthest point to the finish line.
    q = deque([(sy, sx)])
    max_dist = 0  # the longest distance
    gy, gx = 1, 1  # goal positioon
    dx = [1, -1, 0, 0]
    dy = [0, 0, 1, -1]
    # array with the distances of each square
    dist = [[-1]*WIDTH for _ in range(HEIGHT)]
    dist[sy][sx] = 0

    while q:  # Rotate the queue until there are no more elements

        y, x = q.popleft()  # Retrieving an element from the top

        for i in range(4):

            ny = y+dy[i]
            nx = x+dx[i]

            if ny <= 0 or nx <= 0 or ny+1 == HEIGHT or nx+1 == WIDTH:
                continue

            if maze[ny][nx] == "#":
                continue

            if dist[ny][nx] == -1:  # Update the distance if you haven't visited yet
                q.append((ny, nx))
                dist[ny][nx] = dist[y][x]+1

                if max_dist < dist[ny][nx]:  # update the longest distance
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
