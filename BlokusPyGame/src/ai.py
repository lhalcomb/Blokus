from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional

from copy import copy, deepcopy
import math
import random

from color import Color
from board import Board
from player import Player
from piece import Piece


########## Base Agent Class to make code simpler across the ai.py and game.py files ############
class BaseAgent(ABC):
    def __init__(self, player: Player | None): 
        self.player = player
    
    @abstractmethod
    def choose_move(self, board_state: Board) -> Optional[Piece]: 
        """Chooses a move to delegate for simulation"""
        raise NotImplementedError

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

############ Mirror Agent Code ############
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

        player_moves = self._actions_from_state(board_state, self.player) #type: ignore
        opponent_moves = self._actions_from_state(board_state, self.opponent)

        player_mobility = len(player_moves) #type: ignore
        opponent_mobility = len(opponent_moves)
        mobility_score = player_mobility - opponent_mobility; w1 = 0.5 #mobility (building)

        #Layer 3: Opponent corner blocking 
        blocked_corners = self._opponent_corner_blocking(board_state); w2 = 2.0 # aggression (attack)
        

        return (player_score - opponent_score)  + w2 * blocked_corners + w1 * mobility_score

    def _terminal_state(self, board_state: Board) -> bool | None:
        return not ((board_state.player_can_play(self.player) or board_state.player_can_play(self.opponent))) #type: ignore
        
    def _in_bounds(self, x: int, y: int, size: int) -> bool:
        return 0 <= x < size and 0 <= y < size
    
    def _opponent_corner_blocking(self, board_state: Board):
        """ The more blocked corners the better! """
        
        blocked_corners = 0
        diagonals = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
        orthogonals = [(0, -1), (1, 0), (0, 1), (-1, 0)]

        for x in range(board_state.size): #for all (x,y) grid placements
            for y in range(board_state.size):
                if board_state.grid[x][y] == self.opponent.color: #if its the opponent color (2 - orange)
                    for dx, dy in diagonals: #check its diagonals
                        nx, ny = x + dx, y + dy
                        if self._in_bounds(nx, ny, board_state.size): #check if in bounds
                            if board_state.grid[nx][ny] == Color.EMPTY:  #check if zero
                                for ox, oy in orthogonals: #get orthogonals (top, left ,bottom ,right to tile)
                                    px, py = nx + ox, ny + oy
                                    if self._in_bounds(px, py, board_state.size): #check bounds
                                        if board_state.grid[px][py] == self.player.color: #type: ignore (if agents color - up the blocked corner.)
                                            blocked_corners += 1
                                            break  
        return blocked_corners

####### MCTS Agent Code ###########


class MCTSNode: 
    def __init__(self, board_state: Board, parent: MCTSNode | None, action: Piece | None, player: Player):
        self.board_state = board_state
        self.parent = parent
        self.action = action
        self.player = player #current player that made the move
        self.children: list[MCTSNode] = []
        self.visits: int = 0 # number of times a node was visited
        self.wins: float = 0.0  #total reward from simulation
        
        self.untried_actions: list[Piece] = self._actions_from_state(self.board_state, self.player)
    
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

        return possible_moves[:20]

    def _terminal_state(self, board_state: Board, player: Player) -> bool:
        return not board_state.player_can_play(player)
    
    def _is_fully_expanded(self) -> bool:
        return len(self.untried_actions) == 0
    
    def ucb(self, child: MCTSNode, c: float) -> float:
        return (child.wins / child.visits) + (c * math.sqrt(math.log(self.visits)) / child.visits )
    
    def _best_child(self, c: float = math.sqrt(2)):
        for child in self.children: #if you havent visisted the node yet, select it
            if child.visits == 0: 
                return child
        return max(self.children, key = lambda child: self.ucb(child, c))
    

class MCTSAgent(BaseAgent):
    def __init__(self, player: Player, opponent: Player, time: int = 50):
        super().__init__(player)
        self.opponent = opponent
        self.time = time
        self.root: MCTSNode | None = None

    def choose_move(self, board_state: Board) -> Piece | None: #the mcts search
        self.root = MCTSNode(
            board_state=board_state,
            parent=None,
            action=None,       # root has no incoming action
            player= self.player #type: ignore
        )

        for _ in range(self.time):
            node = self._select(self.root)
            node = self._expand(node)
            result = self._simulate(node)
            self._backpropagate(node, result)

        if not self.root.children:
            return None  # no legal moves, pass the turn
        
        # pick the child of root with the most visits
        best = max(self.root.children, key=lambda n: n.visits) 
        return best.action

    def _select(self, node: MCTSNode) -> MCTSNode:

        while not node._terminal_state(node.board_state, node.player ) and node._is_fully_expanded():
            if not node.children:  # fully expanded but no children = terminal
                return node
            node = node._best_child()
        
        return node

    def _expand(self, node: MCTSNode) -> MCTSNode:
        if not node.untried_actions:
            return node
        
        action = node.untried_actions.pop()
        new_state = deepcopy(node.board_state)
        new_state.place_piece(action)

        # deepcopy so each node owns its own player state
        if node.player == self.player:
            next_player = deepcopy(self.opponent)
        else:
            next_player = deepcopy(self.player)

        # also remove the piece from the current node's player in new_state
        current_player = deepcopy(node.player)
        current_player.remove_piece(action.shape)

        child = MCTSNode(new_state, node, action, next_player) #type: ignore
        node.children.append(child)

        return child

    def _simulate(self, node: MCTSNode) -> float:
        board_state = deepcopy(node.board_state)
        
        # deepcopy sim players so we don't mutate the real ones
        sim_player = deepcopy(self.player)
        sim_opponent = deepcopy(self.opponent)
        
        # figure out who goes first in the rollout
        current_sim = sim_player if node.player == self.player else sim_opponent

        while board_state.player_can_play(current_sim): #type: ignore
            actions = node._actions_from_state(board_state, current_sim) #type: ignore

            if not actions:
                break

            action = random.choice(actions)
            board_state.place_piece(action)
            current_sim.remove_piece(action.shape) #type: ignore

            # alternate between the sim copies, not the real players
            current_sim = sim_opponent if current_sim == sim_player else sim_player

        return self._evaluate_terminal_state(board_state)
    
    def _backpropagate(self, node: MCTSNode, result: float) -> None:
        
        while node is not None:
            node.visits += 1
            node.wins += result #accumulate the result (reward)
            node = node.parent #type: ignore
        
    def _evaluate_terminal_state(self, board_state: Board) -> float:
        """Score difference: player_score - opponent_score"""
        player_score = 0
        opponent_score = 0
        
        for x in range(board_state.size):
            for y in range(board_state.size):
                if board_state.grid[x][y] == self.player.color:  # type: ignore
                    player_score += 1
                elif board_state.grid[x][y] == self.opponent.color:
                    opponent_score += 1
        
        return float(player_score - opponent_score)


    



    
