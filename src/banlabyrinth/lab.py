import random
from itertools import filterfalse

WALL = 1
ROAD = 2
letters = {
    (0, -1): 'N',
    (0, 1): 'S',
    (-1, 0): 'W',
    (1, 0): 'E'
}
letters_reversed = {
    'N': (0, -1),
    'S': (0, 1),
    'W': (-1, 0),
    'E': (1, 0)
}


class Node:
    def __init__(self, x, y, walls=None):
        self.x = x
        self.y = y
        self.walls = {(0, -1): 1,
                      (0, 1): 1,
                      (-1, 0): 1,
                      (1, 0): 1} if walls is None else walls

    def neighbour_positions(self, width, height):
        return filter(lambda a: 0 <= a[0] < width and 0 <= a[1] < height,
                      map(lambda a: (self.x + a[0], self.y + a[1]), self.walls.keys()))

    def neighbour_positions_walls(self):
        return map(lambda a: (self.x + a[0], self.y + a[1]),
                   filter(lambda x: self.walls[x] == ROAD, self.walls.keys()))

    def positions(self):
        return self.x, self.y

    def __repr__(self):
        out = "{} {} walls: ".format(self.x, self.y)
        for w in filter(lambda x: self.walls[x] == WALL, self.walls.keys()):
            out += letters[w] + ' '
        return out


class LabyrinthSchema:

    def __init__(self, width, height, matrix_data=None):
        self.matrix = [[Node(x, y) for y in range(height)] for x in range(width)]
        self.width = width
        self.height = height
        if matrix_data is not None:
            characters = map(lambda x: int(x, 16), matrix_data)
            for line in self.matrix:
                for cell in line:
                    number = next(characters)
                    mask = 0b1000
                    for key in sorted(cell.walls.keys()):
                        cell.walls[key] = WALL if number & mask else ROAD
                        mask >>= 1

    def __getitem__(self, item):
        x, y = item
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.matrix[x][y]
        else:
            return None

    def __str__(self):
        out = [['1' for _ in range(2 * self.width + 1)] for _ in range(2 * self.height + 1)]
        for line in self.matrix:
            for elem in line:
                out[2 * elem.y + 1][2 * elem.x + 1] = '.'
                for w_x, w_y in set(filter(lambda x: elem.walls[x] == ROAD, elem.walls.keys())):
                    tw_x, tw_y = 2 * elem.x + 1 + w_x, 2 * elem.y + 1 + w_y
                    out[tw_y][tw_x] = '.'
        return ''.join(map(lambda i: ''.join(i) + '\n', out))
        # return out

    def __repr__(self):
        out = "LabyrinthSchema({}, {}, \'".format(self.width, self.height)
        for line in self.matrix:
            for cell in line:
                number = 0
                for key in sorted(cell.walls.keys()):
                    number = (number << 1) | (cell.walls[key] == WALL)
                out += hex(number)[2]
        return out + '\')'


def randomize_end_position(ls: LabyrinthSchema, strict_longest=True):
    stack = list()
    path = dict()
    dead_ends = list()
    stack.append(ls[(0, 0)])
    path[(0, 0)] = 1
    visited = set()
    visited.add((0, 0))
    while len(stack):
        curr = stack.pop()
        x, y = curr.x, curr.y
        neighbourhood = set(filterfalse(visited.__contains__, curr.neighbour_positions_walls()))
        if len(neighbourhood):
            stack.append(curr)
            stack.extend(map(ls.__getitem__, neighbourhood))
            path.update({i: path[(x, y)] + 1 for i in neighbourhood})
            visited.update(neighbourhood)
        elif len(set(curr.neighbour_positions_walls())) == 1:
            dead_ends.append((path[(x, y)], curr))
    dead_ends.sort(key=lambda a: a[0])
    if strict_longest:
        return dead_ends[-1][1]
    else:
        return random.choice(dead_ends[min(len(dead_ends) // 3 - 1, 1):])[1]


class LabyrinthWalker:
    def __init__(self, ls: LabyrinthSchema, strict_longest=True, start=None, end=None, curr=None):
        self.ls = ls
        self.start = ls[(0, 0)] if start is None else ls[start]
        self.end = randomize_end_position(ls, strict_longest) if end is None else ls[end]
        self.curr = self.start if curr is None else ls[curr]

    def move_into(self, direction: str) -> bool:
        if direction not in letters_reversed:
            raise ValueError("wrong direction")
        if self.is_win():
            return True
        if self.curr.walls[letters_reversed[direction]] == ROAD:
            w_x, w_y = letters_reversed[direction]
            normalized_positions = self.curr.x + w_x, self.curr.y + w_y
            self.curr = self.ls[normalized_positions]
            return True
        else:
            return False

    def is_win(self):
        return self.curr == self.end

    def __str__(self):
        encoded = str(self.ls)
        decoded = [list(i) for i in encoded.split('\n')]
        decoded[2 * self.start.y + 1][2 * self.start.x + 1] = 'S'
        decoded[2 * self.curr.y + 1][2 * self.curr.x + 1] = 'P'
        decoded[2 * self.end.y + 1][2 * self.end.x + 1] = 'E'
        return ''.join(map(lambda i: ''.join(i) + '\n', decoded))

    def __repr__(self):
        return "LabyrinthWalker({},{},{},{},{})".format(repr(self.ls), True, self.start.positions(),
                                                        self.end.positions(), self.curr.positions())


def gen_lab(width, height):
    ls = LabyrinthSchema(width, height)
    visited = set()
    stack = list()
    start = ls[(0, 0)]
    visited.add((0, 0))
    stack.append(start)
    while len(stack):
        curr = stack.pop()
        x, y = curr.x, curr.y
        neighbourhood = list(filterfalse(visited.__contains__, curr.neighbour_positions(width, height)))
        if len(neighbourhood):
            stack.append(curr)
            random_positions = random.choice(neighbourhood)
            r_x, r_y = random_positions
            pxl = ls[random_positions]
            curr.walls[(r_x - x, r_y - y)] = ROAD
            pxl.walls[(x - r_x, y - r_y)] = ROAD
            stack.append(pxl)
            visited.add(random_positions)
    return ls


if __name__ == '__main__':
    example = gen_lab(10, 10)
    print(example)
    print(randomize_end_position(example))
    ex_2 = LabyrinthWalker(example)
    print(ex_2)
    print(repr(example))
    print(repr(eval(repr(example))) == repr(example))
