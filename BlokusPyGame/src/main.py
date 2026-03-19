from game import Game
import argparse

WIDTH, HEIGHT = 800, 800


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-game", choices=["duo", "og"], required=True)
    parser.add_argument("-simulate", action="store_true", help="Run a simulated game instead of interactive one")
    args = parser.parse_args()

    if args.game == "og":
        version = True
        blokus = Game(WIDTH, HEIGHT, version, simulate=args.simulate)
        blokus.run()

    elif args.game == "duo": 
        version = False
        blokusDuo = Game(WIDTH, HEIGHT, version, simulate=args.simulate)
        blokusDuo.run()