from game import Game
import argparse

WIDTH, HEIGHT = 800, 800


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-game", choices=["duo", "og"], required=True)
    parser.add_argument("-simulate", action="store_true", help="Run a simulated game instead of interactive one")
    parser.add_argument("-play_ai", action="store_true", required=False)
    parser.add_argument("-agent_config", choices=["mirror_vs_mirror", "random_vs_random", "random_vs_mirror", "random_vs_minimax"], required=False)
    args = parser.parse_args()

    if args.game == "og":
        version = True
        blokus = Game(WIDTH, HEIGHT, version, simulate=args.simulate)
        blokus.run()

    elif args.game == "duo": 
        version = False
        blokusDuo = Game(WIDTH, HEIGHT, version, num_simulations=5, simulate=args.simulate, play_ai=args.play_ai, agent_config=args.agent_config)
        blokusDuo.run()