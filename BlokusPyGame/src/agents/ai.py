from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional

from engine.board import Board
from engine.piece import Piece
from agents.player import Player


########## Base Agent Class to make code simpler across the ai.py and game.py files ############
class BaseAgent(ABC):
    def __init__(self, player: Player | None): 
        self.player = player
    
    @abstractmethod
    def choose_move(self, board_state: Board) -> Optional[Piece]: 
        """Chooses a move to delegate for simulation"""
        raise NotImplementedError

if __name__ == "__main__":

    print("Testing AI Agents: ")

