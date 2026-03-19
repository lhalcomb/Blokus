from abc import ABC, abstractmethod
import random
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
    def __init__(self, player: Player | None):
        super().__init__(player)

    def choose_move(self, board_state: Board) -> Optional[Piece]:
        """Tries places random pieces until one sticks to a correct position"""
        remaining_pieces_sample = random.sample(self.player.remaining_pieces, len(self.player.remaining_pieces)) # pyright: ignore[reportOptionalMemberAccess]

        for shape in remaining_pieces_sample:
            piece = Piece(shape, self.player.color) #type: ignore
            # if self._try_random_piece(piece, board_state, 5):
            #     return piece
            if self._exhaust_all_possibilities(piece, board_state):
                return piece
            
        return None
    
    def _try_random_piece(self, piece: Piece, board_state: Board, N: int) -> bool: 
        """ Try piece at random positions with rot/flips until sticks"""

        for _ in range(N): #Try an N amount of positions
            piece.set_pos(random.randint(0, board_state.size - 1), 
                          random.randint(0, board_state.size - 1))
            for _ in range(random.randint(0, 1)):
                piece.flip()
            for _ in range(random.randint(0, 3)):
                piece.rotate_cw()
            
            if board_state.can_place_piece(piece):
                return True
            
        return False
    
    def _exhaust_all_possibilities(self, piece: Piece, board_state: Board) -> bool:
        """Exhaust all possibilities of rot/flips until one sticks """
        for x in range(board_state.size):
                for y in range(board_state.size):
                    piece.set_pos(x, y)

                    for _ in range(4):
                        piece.rotate_cw()

                        if board_state.can_place_piece(piece):
                            return True

                    piece.flip()

                    for _ in range(4):
                        piece.rotate_cw()

                        if board_state.can_place_piece(piece):
                            return True
                        
        return False


class MirrorAgent(BaseAgent):
    def __init__(self, player: Player | None, fallback: BaseAgent | None = None): 
        super().__init__(player)

        self.fallback = fallback

    def choose_move(self, board_state: Board) -> Optional[Piece]:
        last_move = None
        opponent_color = [color for color in board_state.last_move_map.keys() if color != self.player.color] # type: ignore
        if opponent_color:
            last_move = board_state.last_move(opponent_color[0])

        if last_move:
            mirrored = self._mirror_move(last_move, board_state)
            if mirrored is not None:
                return mirrored
            
        if self.fallback is not None: 
            return self.fallback.choose_move(board_state)

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
