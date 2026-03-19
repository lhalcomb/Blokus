from abc import ABC, abstractmethod
from typing import Optional
from board import Board
from player import Player
from piece import Piece


class BaseAgent(ABC):
    def __init__(self, player: Player | None): 
        self.player = player
    
    @abstractmethod
    def choose_move(self, board_state: Board) -> Optional[Piece]: 
        """Chooses a move to delegate for simulation"""
        raise NotImplementedError

class RandomAgent(BaseAgent):
    def __init__(self, player: Player):
        super().__init__(player)

    def choose_move(self, board_state: Board) -> Optional[Piece]:
        """Chooses a random piece and places it on the board in a random correct position"""
        pass


class MirrorAgent(BaseAgent):
    def __init__(self, player: Player | None): #fallback: RandomAgent
        super().__init__(player)

        #self.fallback = fallback

    def choose_move(self, board_state: Board) -> Optional[Piece]:
        last_move = None
        opponent_color = [color for color in board_state.last_move_map.keys() if color != self.player.color] # type: ignore
        if opponent_color:
            last_move = board_state.last_move(opponent_color[0])

        if last_move:
            mirrored = self._mirror_move(last_move, board_state)
            if mirrored is not None:
                return mirrored
        return None
        #return self.fallback.choose_move(board_state)

    def _mirror_move(self, last_move: dict, board_state: Board) -> Optional[Piece]:
        """
        Mirror the previously placed move
        """
        board_size: int = board_state.size
        mirror_tiles = [(board_size - 1 - r, board_size - 1 - c) for r,c in last_move['tiles']]
        
        mirror_tiles_set = set(mirror_tiles)
    
        piece = Piece(last_move['shape'], self.player.color) #type: ignore
        
        # Try all rotation and flip combinations
        for flip_count in range(2):  # 0 or 1 flip
            for rotation in range(4):  # 0-3 rotations
                # Set position to minimum coordinates
                min_r = min(r for r, c in mirror_tiles)
                min_c = min(c for r, c in mirror_tiles)
                piece.set_pos(min_r, min_c)
                
                # Check if this rotation/flip matches the mirrored tiles
                if set(piece.tiles()) == mirror_tiles_set:
                    if board_state.can_place_piece(piece):
                        return piece
                
                piece.rotate_cw()
            
            piece.flip()
        
        return None
    

class MiniMaxAgent(BaseAgent):
    def __init__(self, player: Player):
        super().__init__(player)

class AlphaBetaAgent(BaseAgent):
    def __init__(self, player: Player):
        super().__init__(player)

class MCTSAgent(BaseAgent):
    def __init__(self, player: Player):
        super().__init__(player)
