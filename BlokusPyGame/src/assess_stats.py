from save_games import *
import json

from board import Board; from turn import Turn
from ai import *

agents: dict[Color, RandomAgent] = {}

def printPlayerWins(savegame: SaveGame) -> str:

    orangeWins = 0; purpleWins = 0; draws = 0
    with open(savegame.stats_file, "r") as f:
        data = json.load(f)
        
        for item in data:
            if item["winner"] == "Color.ORANGE": 
                orangeWins += 1
            else:
                purpleWins += 1
            for color, score in (item["final_scores"].items()):
                scores = list(item["final_scores"].values())
                if scores[0] == scores[1]:
                    draws += 1

    return f" Orange wins: {orangeWins}, Purple Wins: {purpleWins}, Ties: {draws}"

def countBranchingFactor(num_games: int, verbose: bool) -> float: 
    """ Play a certain number of games, count the number of possible moves at each board_state, return average at the end"""

    all_bfs = []; move_count = 0; game_count = 0

    while num_games > 0:
        turn = Turn(Board(False))
        print(f"Game: {game_count}")
        game_count += 1

        for player in turn.players:
            agents[player.color] = RandomAgent(player)

        while not turn.game_over:
            possible_moves = agents[turn.current_player.color]._actions_from_state(turn.board, turn.current_player) #type: ignore
            all_bfs.append(len(possible_moves))

            if possible_moves:
                move = agents[turn.current_player.color].choose_move(turn.board) #type: ignore
                if move:
                    turn.place_piece(move)
            else: 
                turn.next_turn()
            
            if verbose:
                print(f" Move: {move_count + 1}, # of Possible_Moves: {len(possible_moves)}")
                move_count += 1
        move_count = 0
        num_games -= 1
        


    
    return sum(all_bfs) / len(all_bfs) if all_bfs else 0
    


if __name__ == "__main__":
    # savegame = SaveGame("random_vs_random")
    # printPlayerWins(savegame)

    bfs = countBranchingFactor(1000, True); print(bfs)

    
