import matplotlib.pyplot as plt; import numpy as np
import json; import os

from board import Board; from turn import Turn
from ai import *; from save_games import *

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

            move_count += 1
            if verbose:
                print(f"Game_Count: {game_count} Move: {move_count} , # of Possible_Moves: {len(possible_moves)}")
                
        move_count = 0
        num_games -= 1
        print(f"Game: {game_count} ")
    
    return sum(all_bfs) / len(all_bfs) if all_bfs else 0
    
def plotMoves2Turns(num_games: int, verbose: bool) -> tuple:
    list_list_of_moves = []
    purple_moves_per_game = []  # [[turns for game 1], [turns for game 2], ...]
    orange_moves_per_game = []

    game_count = 0

    while num_games > 0:
        turn = Turn(Board(False))
        
        turn_count = 0

        for player in turn.players:
            agents[player.color] = RandomAgent(player)

        list_of_moves = []
        purple_moves = []
        orange_moves = []
        
        while not turn.game_over:
            possible_moves = agents[turn.current_player.color]._actions_from_state(turn.board, turn.current_player) # type: ignore
            list_of_moves.append(len(possible_moves))

            # Track moves per player
            if turn.current_player.color == Color.PURPLE: #type: ignore
                purple_moves.append(len(possible_moves))
            else:
                orange_moves.append(len(possible_moves))

            if possible_moves:
                move = agents[turn.current_player.color].choose_move(turn.board) #type: ignore
                if move:
                    turn.place_piece(move)
            else: 
                turn.next_turn()

            turn_count += 1
            if verbose and turn.current_player is not None:
                print(f"Game {game_count + 1}, Turn {turn_count}, Player: {turn.current_player.color}, Moves: {len(possible_moves)}") #type: ignore
        game_count += 1

        list_list_of_moves.append(list_of_moves)
        purple_moves_per_game.append(purple_moves)
        orange_moves_per_game.append(orange_moves)
        num_games -= 1

    return list_list_of_moves, purple_moves_per_game, orange_moves_per_game



if __name__ == "__main__":

    src_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(os.path.dirname(src_dir), "assets", "img")
    os.makedirs(assets_dir, exist_ok=True)


    # savegame = SaveGame("random_vs_random")
    # printPlayerWins(savegame)
    num_games = 1000
    #bfs = countBranchingFactor(num_games, False); print(bfs)

    list_list_of_moves, purple_moves_per_game, orange_moves_per_game = plotMoves2Turns(num_games, True)

    # max_turns = max(len(game) for game in list_list_of_moves) #find maximum turns in a game (used for matrix dim)
    # M = np.full((num_games, max_turns), np.nan) # 100 x max_turns matrix filled with np.NaN data types
    # for (game, moves) in enumerate(list_list_of_moves):  #goes through every games moves and fills the columns with move counts (ignores nan values)
    #     M[game, : len(moves)] = moves # if max_turns = 52 then M[0, :45] and M[0, 45:52] are nans
    
    # mean_moves = np.nanmean(M, axis=0) # Average of moves per turn (nanmean ignores nans)
    # p25 = np.nanpercentile(M, 25, axis=0) #25th percentile per turn
    # p75 = np.nanpercentile(M, 75, axis=0) #75th percentile per turn

    # turns = np.arange(1, max_turns + 1) 

    # plt.figure(figsize=(12, 6))
    # plt.plot(turns, mean_moves, linewidth=2, label= f"Mean legal moves per turn ({num_games} games)")
    # plt.fill_between(turns, p25, p75, alpha=0.2, label="25th-75th percentile") #shades the area between the 25th and 75th percentile—shows the spread.

    
    # plt.title(f"Blokus branching factor over turns ({num_games} random games)")
    # plt.xlabel("Turn number")
    # plt.ylabel("Number of legal moves")
    # plt.grid(alpha=0.25)
    # plt.legend()
    # plt.tight_layout()
    # plt.savefig(os.path.join(assets_dir, f"bfover{num_games}.png"), dpi=150, bbox_inches='tight')
    # plt.show()

    #per player
    max_purple_turns = max(len(game) for game in purple_moves_per_game)
    max_orange_turns = max(len(game) for game in orange_moves_per_game)
    
    M_purple = np.full((num_games, max_purple_turns), np.nan)
    M_orange = np.full((num_games, max_orange_turns), np.nan)
    
    for i, moves in enumerate(purple_moves_per_game):
        M_purple[i, :len(moves)] = moves
    for i, moves in enumerate(orange_moves_per_game):
        M_orange[i, :len(moves)] = moves
    
    mean_purple = np.nanmean(M_purple, axis=0)
    mean_orange = np.nanmean(M_orange, axis=0)
    
    turns_purple = np.arange(1, max_purple_turns + 1)
    turns_orange = np.arange(1, max_orange_turns + 1)

    plt.figure(figsize=(12, 6))
    plt.plot(turns_purple, mean_purple, linewidth=2, label="Purple avg moves", color='purple')
    plt.plot(turns_orange, mean_orange, linewidth=2, label="Orange avg moves", color='orange')
    
    plt.title(f"Blokus moves per player ({num_games} games)")
    plt.xlabel("Turn number (per player)")
    plt.ylabel("Number of legal moves")
    plt.grid(alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(assets_dir, f"moves_per_player_{num_games}.png"), dpi=150, bbox_inches='tight')
    plt.show()

    
