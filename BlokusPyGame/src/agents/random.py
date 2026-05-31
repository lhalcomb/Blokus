
from __future__ import annotations
from agents.ai import BaseAgent

from typing import Optional
from copy import deepcopy
import random

from engine.board import Board
from engine.piece import Piece
from agents.player import Player

############ Random Agent Code ############
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
    
    def _actions_from_state(self, board_state: Board, player: Player) -> list[Piece]:  #type: ignore
        #sees if a move can be placed, then returns the biggest pieces first
        possible_moves: list[Piece] = []

        #1. Exhaust all piece placements to see what sticks && 
        #2. Avoid adding duplicate pieces

        seen = set()
        for shape in player.remaining_pieces:
            piece = Piece(shape, player.color)

            # then iterate positions/rotations on this fresh piece
            for x in range(board_state.size):
                for y in range(board_state.size):
                    piece.set_pos(x, y)

                    for rotations, flipped in board_state._get_orientations(shape):
                        piece.rotations = rotations
                        piece.flipped = flipped

                        if board_state.can_place_piece(piece):
                            key = (shape, piece.x, piece.y, piece.rotations, piece.flipped)
                            if key not in seen: 
                                seen.add(key)
                                possible_moves.append(deepcopy(piece))

    
        #3. Sort the pieces in descending order
        possible_moves = sorted(possible_moves, key=lambda piece: piece.size(), reverse=True)

        return possible_moves