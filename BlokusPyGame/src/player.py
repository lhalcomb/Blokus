from color import Color


class Player:
    def __init__(self, color: Color):
        self.remaining_pieces: list = []
        self.color: Color = color

    def choose_color(self):
        pass
