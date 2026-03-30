from abc import ABC, abstractmethod
from copy import copy, deepcopy
import math
import random
from typing import Optional

from color import Color
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
        print(mirror_tiles)
    
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
    """ Tuned with alpha beta pruning for better search. """
    def __init__(self, player: Player, opponent: Player):
        super().__init__(player)
        self.opponent = opponent
        self.depth = 2

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

        #1. Exhaust all piece placements to see what sticks
        for shape in player.remaining_pieces:
            piece = Piece(shape, player.color)

            # then iterate positions/rotations on this fresh piece
            for x in range(board_state.size):
                    for y in range(board_state.size):
                        piece.set_pos(x, y)

                        for _ in range(4):
                            piece.rotate_cw()

                            if board_state.can_place_piece(piece):
                                
                                possible_moves.append(deepcopy(piece))

                        piece.flip()

                        for _ in range(4):
                            piece.rotate_cw()

                            if board_state.can_place_piece(piece):
                                
                                possible_moves.append(deepcopy(piece))

        #2. Avoid adding duplicate pieces
        #develop later, research set and frozen set

        #3. Sort the pieces in descending order
        possible_moves = sorted(possible_moves, key=lambda piece: piece.size(), reverse=True)

        return possible_moves[:20]


    def _value(self, board_state: Board) -> float:
        #Works in 3 layers

        #Layer 1: Get the difference in player vs opponent score for each min and max 

        player_score = 0; opponent_score = 0

        for x in range(board_state.size):
            for y in range(board_state.size):
                if board_state.grid[x][y] == self.player.color:  #type: ignore
                    player_score += 1
                elif board_state.grid[x][y] == self.opponent.color: 
                    opponent_score += 1
        
        #Layer 2: Count all the valid moves for mobility score (Constraint of piece placement)
        #The more options after a player places a piece, the more power (score)

        # player_mobility = len(self._actions_from_state(board_state, self.player)) #type: ignore
        # opponent_mobility = len(self._actions_from_state(board_state, self.opponent))
        # mobility_score = player_mobility - opponent_mobility; w1 = 0.5 #mobility (building)

        #Layer 3: Opponent corner blocking 
        blocked_corners = self._opponent_corner_blocking(board_state); w2 = 2.0 # aggression (attack)
        

        return (player_score - opponent_score)  + w2 * blocked_corners #+ w1 * mobility_score

    def _terminal_state(self, board_state: Board) -> bool | None:
        return not ((board_state.player_can_play(self.player) or board_state.player_can_play(self.opponent))) #type: ignore
        

    def _opponent_corner_blocking(self, board_state: Board):
        blocked_corners = 0
        for x in range(board_state.size):
            for y in range(board_state.size):
                diagonals_ = [(x-1, y-1), (x-1, y+1), (x+1, y-1), (x+1, y+1)]
                if board_state.grid[x][y] == self.opponent.color:
                    for dx, dy in diagonals_:
                        if 0 <= dx < board_state.size and 0 <= dy < board_state.size:
                            if board_state.grid[dx][dy] == Color.EMPTY: 
                                orthogonals = [(dx-1, dy), (dx+1, dy), (dx, dy-1), (dx, dy+1)]
                                
                                for ox, oy in orthogonals:
                                    if 0 <= ox < board_state.size and 0 <= oy < board_state.size:
                                        if board_state.grid[ox][oy] == self.player.color: #type: ignore
                                            blocked_corners += 1
                                            break  # why break here?
        
        return blocked_corners
    
class MCTSAgent(BaseAgent):
    def __init__(self, player: Player):
        super().__init__(player)
