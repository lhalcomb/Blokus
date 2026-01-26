

"rmk: @staticmethod lets me do class.method without having to invoke the object first. (i.e. class = class())"

class Piece:
    """
    This class controls the piece logic. 

    I structured the pieces in arrays of 2-Tuples ranging from
    1-5 in size. One tuple represents one polyomino tile.

    Polyomino Grid:  (x, y) x - row, y - col

    (4, 0), (4, 1), (4, 2), (4, 3), (4, 4)
    (3, 0), (3, 1), (3, 2), (3, 3), (3, 4)
    (2, 0), (2, 1), (2, 2), (2, 3), (2, 4)
    (1, 0), (1, 1), (1, 2), (1, 3), (1, 4)
    (0, 0), (0, 1), (0, 2), (0, 3), (0, 4)

    """

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
    def __init__(self, shape, color):
       self.shape = shape #Piece dict key: List of x, y coordinates relative to origin
       self.shape_val = self.BASE_PIECES[shape]
       self.color = color #playerID (1-4)
    
    @staticmethod
    def rotate(shape):
        """  
        Takes in shape as input and rotates shape 90° clockwise
        """
        return [(-y, x) for x, y in shape]
    
    @staticmethod
    def flip(shape):        
        """  
        Takes in shape as input and flips it horizontally
        """
        return [(-x, y) for x, y in shape]
    
    @staticmethod
    def normalize(shape):
        """
        Normalizes the shape after the transformation
        
        :param shape: Array of 2-Tuples ranging 1-5
        """
        min_x = min(x for x,_ in shape)
        min_y = min(y for _,y in shape)

        return [(x - min_x, y - min_y) for x, y in shape]
    
    def transformed(self, rotations=0, flipped=False): 
        """
        Return a normalized copy of this piece's shape after applying
        the given rotations (90° steps clockwise) and optional horizontal flip.
        The returned coordinates are shifted so min x and min y are 0.

        """

        shape = list(self.shape_val)
        for _ in range(rotations % 4):
            shape = self.rotate(shape)# 90° each time
        if flipped:
            shape = self.flip(shape)# mirror horizontally
        return self.normalize(shape)
