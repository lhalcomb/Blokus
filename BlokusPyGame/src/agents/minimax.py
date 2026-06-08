from __future__ import annotations
from agents.ai import BaseAgent

from copy import deepcopy
import math
import numpy as np

from utils.color import Color
from engine.board import Board
from engine.piece import Piece
from agents.player import Player


############ MiniMax Code ############
class MiniMaxAgent(BaseAgent): 
    """ Tuned with alpha beta pruning for better search. """
    def __init__(self, player: Player, opponent: Player):
        super().__init__(player)
        self.opponent = opponent
        self.depth = 1

    def choose_move(self, board_state: Board) -> Piece | None:
        best_move = None; best_value = -math.inf

        for action in self._actions_from_state(board_state, self.player): #type: ignore
            board_state.place_piece(action)
            self.player.remove_piece(action.shape) #type: ignore
            score = self._alpha_beta_minimax(board_state, self.depth, -math.inf, math.inf, False)
            board_state.unplace_piece(action)
            self.player.remaining_pieces.append(action.shape)#type: ignore

            if score > best_value:
                best_value = score
                best_move = action

        #print(self.player.remaining_pieces) #type: ignore
        return best_move

    def _alpha_beta_minimax(self, board_state: Board,  depth: int, alpha: int | float, beta: int | float, is_maxing: bool) -> int | float:
        
        if self._terminal_state(board_state) or depth == 0:
            return self._value(board_state)
        
        if is_maxing: #type: ignore
            value = -math.inf
            for action in self._actions_from_state(board_state, self.player): #type: ignore
                
                board_state.place_piece(action)
                self.player.remove_piece(action.shape) #type: ignore

                value = max(value, self._alpha_beta_minimax(board_state, depth - 1, alpha, beta, False))
                board_state.unplace_piece(action)
                self.player.remaining_pieces.append(action.shape) #type: ignore

                alpha = max(alpha, value)
                
                if beta <= alpha:
                    break
            return value
        
        else: #type: ignore

            value = math.inf
            for action in self._actions_from_state(board_state, self.opponent): #type: ignore

                board_state.place_piece(action)
                self.opponent.remove_piece(action.shape) #type: ignore
                value = min(value, self._alpha_beta_minimax(board_state, depth - 1, alpha, beta, True))
                board_state.unplace_piece(action)
                self.opponent.remaining_pieces.append(action.shape)
                beta = min(beta, value)
                if beta <= alpha:
                    break

            return value
        

    def _actions_from_state(self, board_state: Board, player: Player) -> list[Piece]:  #type: ignore
        #sees if a move can be placed, then returns the biggest pieces first
        possible_moves: list[Piece] = []
        #1. Exhaust all piece placements to see what sticks && 
        #2. Avoid adding duplicate pieces 
        seen = set()
        for shape in player.remaining_pieces:
            piece = Piece(shape, player.color)

            # then iterate positions/rotations on this fresh piece
            for idx in range(board_state.size * board_state.size):
                (x,y) = idx % board_state.size, idx // board_state.size
                piece.set_pos(x, y)

                for rotations, flipped in board_state.get_orientations(shape):
                    piece.rotations = rotations
                    piece.flipped = flipped

                    if board_state.can_place_piece(piece):
                        key = (shape, piece.x, piece.y, piece.rotations, piece.flipped)
                        if key not in seen: 
                            seen.add(key)
                            possible_moves.append(deepcopy(piece))

        #3. Sort the pieces in descending order
        possible_moves = sorted(possible_moves, key=lambda piece: piece.size(), reverse=True)

        return possible_moves[:20]


    def _value(self, board_state: Board) -> float:
        #dude numpy ftw!!

        #Works in 3 layers

        #Layer 1: Get the difference in player vs opponent score for each min and max 

        # player_score = 0; opponent_score = 0

        # for idx in range(board_state.size * board_state.size): 
        #     if board_state.grid[idx] == self.player.color: #type: ignore
        #         player_score += 1
        #     elif board_state.grid[idx] == self.opponent.color: 
        #         opponent_score += 1

        player_score = np.sum(board_state.grid == self.player.color) #type: ignore
        opponent_score = np.sum(board_state.grid == self.opponent.color)
        
        #Layer 2: Count all the valid moves for mobility score (Constraint of piece placement)
        #The more options after a player places a piece, the more power (score)

        player_moves = self._actions_from_state(board_state, self.player) #type: ignore
        opponent_moves = self._actions_from_state(board_state, self.opponent)
        mobility_score = (len(player_moves) - len(opponent_moves)) * 0.5 #mobility (building)

        #Layer 3: Opponent corner blocking 
        blocked_corners = self._opponent_corner_blocking(board_state) * 2.0 # aggression (attack)
        

        return (player_score - opponent_score) + blocked_corners + mobility_score

    def _terminal_state(self, board_state: Board) -> bool | None:
        return not ((board_state.player_can_play(self.player) or board_state.player_can_play(self.opponent))) #type: ignore
        
    def _in_bounds(self, x: int, y: int, size: int) -> bool:
        return 0 <= x < size and 0 <= y < size
    
    def _opponent_corner_blocking(self, board_state: Board):
        """ The more blocked corners the better! """
        
        blocked_corners = 0
        diagonals = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
        orthogonals = [(0, -1), (1, 0), (0, 1), (-1, 0)]

        # numpy ftw AGAIN!
        opponent_indices = np.where(board_state.grid == self.opponent.color)[0]

        for idx in opponent_indices: #for all (idx) grid placements
            x = idx % board_state.size
            y = idx // board_state.size

        
            for dx, dy in diagonals: #check its diagonals
                nx, ny = x + dx, y + dy
                if self._in_bounds(nx, ny, board_state.size): #check if in bounds
                    n_idx = nx + ny * board_state.size
                    if board_state.grid[n_idx] == Color.EMPTY:  #check if zero
                        for ox, oy in orthogonals: #get orthogonals (top, left ,bottom ,right to tile)
                            px, py = nx + ox, ny + oy
                            if self._in_bounds(px, py, board_state.size): #check bounds
                                p_idx = px + py * board_state.size
                                if board_state.grid[p_idx] == self.player.color: #type: ignore (if agents color - up the blocked corner.)
                                    blocked_corners += 1
                                    break  
        return blocked_corners