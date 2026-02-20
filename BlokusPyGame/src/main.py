from game import Game
import argparse

WIDTH, HEIGHT = 800, 800


if __name__ == "__main__":
    
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