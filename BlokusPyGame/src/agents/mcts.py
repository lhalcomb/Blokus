from __future__ import annotations
from typing import Optional
from agents.ai import BaseAgent 

from copy import deepcopy
import math
import numpy as np
import random
# import heapq

from utils.dsa import MaxHeap as mh

from engine.board import Board
from engine.piece import Piece
from engine.move_gen import actions_from_state
from agents.player import Player

ACTIONS_C = 30 #actions to collect 


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
        
        self.untried_actions: list[Piece] = actions_from_state(self.board_state, self.player, ACTIONS_C)
    
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

            action = random.choice(actions) #Change this to value & policy network for an alpha zero version
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
        #numpy is goated

        player_score = np.sum(board_state.grid == self.player.color) #type: ignore
        opponent_score = np.sum(board_state.grid == self.opponent.color)
        
        return float(player_score - opponent_score)


    



    
