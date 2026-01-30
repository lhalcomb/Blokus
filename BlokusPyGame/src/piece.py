class Piece:
    BASE_PIECES = { # the 21 possible polyomino shapes (w/o transformations)
        'I1': [(0, 0)],  # Single square
        'I2': [(0, 0), (1, 0)],  # Domino
        'I3': [(0, 0), (1, 0), (2, 0)],  # Straight 3
        'L3': [(0, 0), (1, 0), (1, 1)],  # L-shape 3
        'I4': [(0, 0), (1, 0), (2, 0), (3, 0)], #Straight 4
        'L4': [(0, 0), (1, 0), (2, 0), (2, 1)], #L-shape 4
        'N4': [(1, 0), (1, 1), (0, 1), (0, 2)], #N-Shape 4
        'O4': [(0, 0), (1, 0), (0, 1), (1, 1)], #O-Shape 4
        'T4': [(1, 0), (0, 1), (1, 1), (1, 2)], #T-Shape 4
        'F5': [(1, 0), (0, 1), (1, 1), (1, 2), (2, 2)], #F-Shape 5
        'I5': [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)], #I-shaped 5
        'L5': [(0, 0), (1, 0), (2, 0), (3, 0), (3, 1)], #L-Shaped 5
        'N5': [(0, 0), (1, 0), (2, 0), (2, 1), (3, 1)], #N-Shaped 5
        'P5': [(0, 0), (1, 0), (2, 0), (1, 1), (2, 1)], #P-Shaped 5
        'T5': [(0, 1), (1, 1), (2, 1), (2, 0), (2, 2)], #T-Shaped 5
        'U5': [(0, 0), (1, 0), (0, 1), (0, 2), (1, 2)], #U-Shape 5
        'V5': [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2)], #V-Shape 5
        'W5': [(0, 0), (0, 1), (1, 1), (1, 2), (2, 2)], #W-Shape 5
        'X5': [(0, 1), (1, 0), (1, 1), (1, 2), (2, 1)], #X-Shape 5
        'Y5': [(0, 1), (1, 1), (1, 2), (1, 3), (0, 2)], #Y-Shape 5
        'Z5': [(2, 0), (0, 1), (0, 2), (1, 1), (1, 2)], #Z-shape 5
    }

    COLORS = [
        (200, 200, 200), # Empty
        (255, 0, 0), # Red
        (255, 255, 0), # Yellow
        (0, 255, 0), # Green
        (0, 0, 255) # Blue
    ]

    def __init__(self, shape: str, color: int):
       self.shape: str = shape
       self.color: int = color # 1-4
       self.x: int = 0
       self.y: int = 0
       self.rotations: int = 0 # 0-3
       self.flipped: bool = False

    def set_pos(self, x: int, y: int):
        self.x = x
        self.y = y

    def rotate_cw(self):
        self.rotations += 1

        if self.rotations > 3:
            self.rotations = 0

    def rotate_ccw(self):
        self.rotations -= 1

        if self.rotations < 0:
            self.rotations = 3

    def flip(self):
        self.flipped = not self.flipped

    def cells(self):
        shape = self.BASE_PIECES[self.shape]

        for _ in range(self.rotations):
            shape = [(-y, x) for x, y in shape]

        if self.flipped:
            shape = [(-x, y) for x, y in shape]

        shape = [(x + self.x, y + self.y) for x, y in shape]
        return shape
