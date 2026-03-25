"""
This file is used to save different kinds of game simulations based upon different agents and gameplay strategies.
This creates consistency across all forms of gameplay. 

"""

import json; import os
from datetime import datetime
from enum import Enum

class SaveGame:

    def __init__(self, agent_config: str, data_dir: str = ""):

        self.agent_config = agent_config
        if data_dir is "":
            src_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(src_dir)
            data_dir = os.path.join(parent_dir, "game_data")

        self.data_dir = data_dir
        self.stats_file = self._setup_directory()

    
    def set_stats(self, bits_per_cell: int, board, turn):
       
       stats = {
            "timestamp": datetime.now().isoformat(),
            "board_version": "4-player" if board.version else "2-player",
            "final_scores": {str(color): score for color, score in turn.scores.items()},
            "winner": str(max(turn.scores, key=lambda color: turn.scores[color])),
            "board_state": self._board_to_bitstring(board.print_grid().tolist(), bits_per_cell)
        
        }
       
       return stats
    
    def save_stats(self, stats: list):

        if not isinstance(stats, list):
            stats = [stats]
    
        existing_stats = self._load_existing_stats()
        all_stats = existing_stats + stats

        with open(self.stats_file, 'w') as f:
            json.dump(all_stats, f, indent=2)
        
        total = len(all_stats)
        new_count = len(stats)
        print(f"Saved {new_count} games. Total games in {self.agent_config}: {total}")
        
    def count_wins_ties(self):
        orangeWins = 0; purpleWins = 0; draws = 0

        with open(self.stats_file, "r") as f:
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
        print(f" Orange wins: {orangeWins}, Purple Wins: {purpleWins}, Ties: {draws}")

    def _setup_directory(self) -> str:
        path = os.path.join(self.data_dir, self.agent_config)
        os.makedirs(path, exist_ok=True)
        return os.path.join(path, "games.json")

    def _load_existing_stats(self) -> list:
        try:
            with open(self.stats_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
        
    def get_stats_file_path(self) -> str:
        return self.stats_file
    
    ### Helper Functions for storing board ###
    def _board_to_bitstring(self, board, bits_per_cell):
        """Convert board to bitstring"""
        bits = ''
        for row in board:
            for cell in row:
                bits += format(cell, f'0{bits_per_cell}b')
        return bits

    def _bitstring_to_board(self, bitstring, size, bits_per_cell):
        """Convert bitstring back to board"""
        board = []
        for i in range(size):
            row = []
            for j in range(size):
                idx = (i * size + j) * bits_per_cell
                cell_bits = bitstring[idx:idx+bits_per_cell]
                row.append(int(cell_bits, 2))
            board.append(row)
        return board