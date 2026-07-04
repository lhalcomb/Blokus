
# type: ignore
from __future__ import annotations
from collections import defaultdict
from typing import Optional
from agents.ai import BaseAgent 

from copy import deepcopy
import math
import numpy as np
import random

from engine.move_gen import actions_from_state
from utils.dsa import MaxHeap as mh
from utils.color import Color

from engine.board import Board
from engine.piece import Piece
from engine.turn import Turn
from agents.player import Player

ACTIONS_C = 25 #actions to collect

class MPAgent(BaseAgent):
    

    def __init__(self, player: Player, opponent: Player, turn: Turn):
        super().__init__(player)
        self.opponent = opponent
        self.turn = turn

        self.state_idx = {}   # tuple → int
        self.idx_state = []   # int → tuple
        self.Mk = None

    def choose_move(self, board_state: Board) -> Piece | None: 
        if self.Mk is None:
            return self._greedy_fallback(board_state)
        
        best_action = None
        best_value = -math.inf

        # fall back if the state we find wasn't visited in rollout
        # just select the move with the best free diagonals at that move
        best_greedy_action = None
        best_diag_count = -math.inf

        for action in actions_from_state(board_state, self.player, ACTIONS_C):
            sim_board = deepcopy(board_state)
            sim_board.place_piece(action)
            valid_diag = len(sim_board.valid_diagonals[self.player.color])

            # collect the greedy fallback action regardless if state exists or not
            if valid_diag > best_diag_count:
                best_diag_count = valid_diag
                best_greedy_action = action

            #markov process lookup
            s_abs = self._abstract_state(sim_board)

            if s_abs not in self.state_idx:
                continue # skip all states not seen yet

            i = self.state_idx[s_abs]
            value = self.Mk[i, -1]

            if value > best_value:
                best_value = value 
                best_action = action

        if best_action is None:
            best_action = best_greedy_action
            
        return best_action


    # def _markov_agent_action(self, board_state: Board, Mk: np.ndarray): 
        
    
    ### Private Methods ### 
    def _abstract_state(self, game_state: Board) -> tuple: 
        
        # Frontier Diagonals for each player
        purple_diag = len(game_state.valid_diagonals[Color.PURPLE])
        orange_diag = len(game_state.valid_diagonals[Color.ORANGE])

        # Bucket Diagonals for lowering state space
        purple_diag_bin = min(purple_diag, 20) // 4   # bins: 0-4
        orange_diag_bin = min(orange_diag, 20) // 4

        # Score delta (who is ahead and by how much)
        purple_score = int(np.sum(game_state.grid == Color.PURPLE))
        orange_score = int(np.sum(game_state.grid == Color.ORANGE))
        delta = purple_score - orange_score
        delta_bin = max(-3, min(3, delta // 10))       # bins: -3 to 3

        # --- Pieces remaining ---
        purple_pieces = len(self.player.remaining_pieces)
        orange_pieces = len(self.opponent.remaining_pieces)
        purple_pieces_bin = min(purple_pieces, 21) // 4  # bins: 0-5
        orange_pieces_bin = min(orange_pieces, 21) // 4

        return (
            purple_diag_bin,
            orange_diag_bin,
            delta_bin,
            purple_pieces_bin,
            orange_pieces_bin,
        )


    def _run_rollout(self, initial_board: Board) -> list[tuple[tuple, tuple, float]]:
        board = deepcopy(initial_board)
        sim_player = deepcopy(self.player)
        sim_opponent = deepcopy(self.opponent)
        current = sim_player
        transitions = []

        while board.player_can_play(current): 
            actions = actions_from_state(board, current, ACTIONS_C)
            if not actions:
                break

            s_abs = self._abstract_state(board)
            action = random.choice(actions)
            board.place_piece(action)
            current.remove_piece(action.shape)
            s_abs_next = self._abstract_state(board)

            transitions.append((s_abs, s_abs_next, None))  # None reward is filler bc we are collecting states at the end
            current = sim_opponent if current == sim_player else sim_player # swap player to be simulated

        # Compute the reward for the simulated end game 
        terminal_reward = float(
            np.sum(board.grid == self.player.color) -
            np.sum(board.grid == self.opponent.color)
        )

        # Backfill reward into every transition
        return [(s, s_next, terminal_reward) for s, s_next, _ in transitions]
    
    

    def _get_or_add_state(self, s):
        if s not in self.state_idx:
            self.state_idx[s] = len(self.idx_state)
            self.idx_state.append(s)
        return self.state_idx[s]
    
    def _collect_transitions(self, initial_board: Board, n_rollouts: int = 200) -> list[tuple[tuple, tuple, float]]:
        all_transitions = []
        for _ in range(n_rollouts):
            all_transitions.extend(self._run_rollout(initial_board))
        return all_transitions
    
    def _build_transition_matrix(self, board: Board):
        # builds the transition matrix P using the above methods
        # uses simple frequency method of obtaining probabilities from the abstract states idea

        counts = defaultdict(lambda: defaultdict(int)) # amount of times we see states transition
        reward_sums = defaultdict(float) # sum of rewards for each state
        reward_counts = defaultdict(int) # amount of rewards for each state

        for (s_abs, s_abs_next, reward) in self._collect_transitions(board): 
            i = self._get_or_add_state(s_abs)
            j = self._get_or_add_state(s_abs_next)
            reward_sums[i] += reward
            reward_counts[i] += 1
            counts[i][j] += 1

        n = len(self.state_idx)

        # Build the reward vector     
        r = np.zeros(n) # mean reward observed in each abstract state
        for i in range(n):
            if reward_counts[i] > 0:
                r[i] = reward_sums[i] / reward_counts[i]
        
        P = np.zeros((n, n)) # transition matrix we're building (raw counts to row-stochastic matrix P)

        for i in range(n):
            row_sum = sum(counts[i].values())
            if row_sum == 0: # uniform row to avoid division by zero
                P[i] = 1/n
            else:
                for j, count in counts[i].items():
                    P[i][j] = count / row_sum

        return P.reshape(n,n), r.reshape(n)

    def _matrix_pow(self, M, k):
        # the meat and potatoes
        # built for quick O(k^3 log n) matrix exponentation for fast computation of transtition probabilities

        result = np.identity(M.shape[0])
        base = M

        while k > 0:
            if k & 1:
                result = result @ base    # "collect" this power
            base = base @ base            # square it for next bit
            k = k // 2                    # shift to next bit

        return result
    
    def _build_augment_matrix(self, P, r):
        n = P.shape[0]
        M = np.zeros((n + 1, n + 1))

        M[:n, :n] = P
        M[:n, -1] = r
        M[n, n] = 1

        return M
    
    def _precompute_Mk(self, P, r, k): 
        M = self._build_augment_matrix(P, r)
        Mk = self._matrix_pow(M, k)
        return Mk


### Possible changes ###

    # def _run_rollout(self, initial_board: Board) -> list[tuple[tuple, tuple, float]]:

    #     board = deepcopy(initial_board)
    #     sim_player = deepcopy(self.player)
    #     sim_opponent = deepcopy(self.opponent)
    #     current = sim_player
    #     transitions = []

    #     while board.player_can_play(current): #type: ignore
           
    #         actions = actions_from_state( 
    #              board, current, #type: ignore
    #              ACTIONS_C
    #         )
    #         if not actions:
    #             break

    #         s_abs = self._abstract_state(board)
    #         action = random.choice(actions)
    #         board.place_piece(action)
    #         current.remove_piece(action.shape) #type: ignore
    #         s_abs_next = self._abstract_state(board)

    #         # Intermediate reward: tile delta after this move
    #         reward = float(
    #             np.sum(board.grid == self.player.color) - #type: ignore
    #             np.sum(board.grid == self.opponent.color)
    #         )

    #         transitions.append((s_abs, s_abs_next, reward))
    #         current = sim_opponent if current == sim_player else sim_player

    #     gamma = 0.95

    #     filled = []
    #     T = len(transitions)
    #     for i, (s, s_next, _) in enumerate(transitions):
    #         steps_to_end = T - i
    #         discounted = terminal_reward * (gamma ** steps_to_end)
    #         filled.append((s, s_next, discounted))
    #     return filled


if __name__ == "__main__":
    from agents.random import RandomAgent

    version = False
    board = Board(version)
    turn = Turn(board)
    players = list(turn.players)
    player1, player2 = players[0], players[1]
    ra = RandomAgent(player1)
    markov_p = MPAgent(player1, player2, turn)

    #print(markov_p._abstract_state(board))
    #print(markov_p._run_rollout(board))
    #print(markov_p._collect_transitions(board)[0])
    #P, r = markov_p._build_transition_matrix(board)
    # print(f"Probability Transitions Matrix: {P}")
    # print(f"Reward Vector: {r}")
    # rng = np.random.default_rng()
    # floats_2d = rng.random((2, 2))
    # floats_1d = rng.random(2)
    # print(markov_p._matrix_pow(floats_2d, 2))
    # print(markov_p._build_augment_matrix(floats_2d, floats_1d))

    # Going to need in game.py for future use
    # P, r = agent.build_transition_matrix(board)
    # agent.Mk = agent._precompute_Mk(P, r, k=20)
    # agent.choose_move(board) 
    