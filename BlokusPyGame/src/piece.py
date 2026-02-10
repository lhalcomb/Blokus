from color import Color

PIECES = {
    'I1': [(0, 0)],
    'I2': [(0, 0), (1, 0)],
    'I3': [(0, 0), (1, 0), (2, 0)],
    'L3': [(0, 0), (1, 0), (0, 1)],
    'I4': [(0, 0), (1, 0), (2, 0), (3, 0)],
    'L4': [(0, 0), (1, 0), (0, 1), (0, 2)],
    'N4': [(0, 0), (0, 1), (1, 1), (1, 2)],
    'O4': [(0, 0), (1, 0), (0, 1), (1, 1)],
    'T4': [(0, 0), (1, 0), (2, 0), (1, 1)],
    'F5': [(0, 0), (1, 0), (1, 1), (2, 1), (1, 2)],
    'I5': [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)],
    'L5': [(0, 0), (1, 0), (2, 0), (3, 0), (0, 1)],
    'N5': [(0, 0), (1, 0), (2, 0), (2, 1), (3, 1)],
    'P5': [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1)],
    'T5': [(0, 0), (1, 0), (2, 0), (1, 1), (1, 2)],
    'U5': [(0, 0), (1, 0), (2, 0), (0, 1), (2, 1)],
    'V5': [(0, 0), (1, 0), (2, 0), (0, 1), (0, 2)],
    'W5': [(0, 0), (0, 1), (1, 1), (1, 2), (2, 2)],
    'X5': [(1, 0), (0, 1), (1, 1), (2, 1), (1, 2)],
    'Y5': [(0, 0), (1, 0), (2, 0), (3, 0), (1, 1)],
    'Z5': [(0, 0), (1, 0), (1, 1), (1, 2), (2, 2)],
}


def normalize(shape):
    min_x = min(x for x, y in shape)
    min_y = min(y for x, y in shape)

    shape = [(x - min_x, y - min_y) for x, y in shape]

    return shape


class Piece:
    def __init__(self, shape: str, color: Color):
        self.shape: str = shape
        self.color: Color = color
        self.x: int = 0
        self.y: int = 0
        self.rotations: int = 0  # 0-3
        self.flipped: bool = False

    def set_pos(self, x: int, y: int):
        self.x = x
        self.y = y

    def rotate_cw(self):
        self.rotations = (self.rotations + 1) % 4

    def rotate_ccw(self):
        self.rotations = (self.rotations - 1) % 4

    def flip(self):
        self.flipped = not self.flipped

    def tiles(self):
        shape = PIECES[self.shape]

        for _ in range(self.rotations):
            shape = [(-y, x) for x, y in shape]

        if self.flipped:
            shape = [(-x, y) for x, y in shape]

        return [(x + self.x, y + self.y) for x, y in normalize(shape)]

    def size(self):
        tiles = self.tiles()
        min_x = min(x for x, _ in tiles)
        min_y = min(y for _, y in tiles)

        return max(x for x, _ in tiles) - min_x, max(y for _, y in tiles) - min_y
