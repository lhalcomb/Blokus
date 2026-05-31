import argparse
from test import Game #type: ignore

if __name__ == "__main__":

    
    # board_1d = np.array(board)
    # starting_corners: dict[Color, int] = {
    #         Color.BLUE: 0,
    #         Color.YELLOW: size - 1,
    #         Color.RED: (size ** 2) - 1,
    #         Color.GREEN: (size ** 2) - (size),
    #     } if version else {
    #         Color.PURPLE: (4 * size) + 4,
    #         Color.ORANGE: ((size * size) - (4 * size)) - 5,
    #     }
    # board_1d[((size * size) - (4 * size)) - 5] = 1
    # board_1d[(4 * size) + 4] = 1
    # print(starting_corners[Color.ORANGE])
    # print(board_1d.reshape(size, size))
    
   
    WIDTH, HEIGHT = 800, 800
        
    parser = argparse.ArgumentParser()
    parser.add_argument("-game", choices=["duo", "og"], required=True)
    args = parser.parse_args()

    if args.game == "og":
        version = True
        blokus = Game(WIDTH, HEIGHT, version)
        blokus.run()

    elif args.game == "duo": 
        version = False
        blokusDuo = Game(WIDTH, HEIGHT, version)
        blokusDuo.run() 