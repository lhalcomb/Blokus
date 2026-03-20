import pygame
import json
from datetime import datetime

from board import Board
from turn import Turn
from ui import UI
from ai import *


class Game:
    def __init__(self, width: int, height: int, version: bool, simulate: bool):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption('Blokus')

        self.simulate = simulate
        self.clock = pygame.time.Clock()
        self.running = True
        self.board = Board(version)
        self.turn = Turn(self.board)
        self.ui = UI(pygame.display.set_mode((width, height)), self.board, self.turn)

    def run(self):
        if self.simulate:
            self._run_simulation()
        else: 
            self._run_interactive()
    
    def _run_interactive(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.running = False
                    if event.key == pygame.K_b:
                        self.board.print_board()

                self.ui.handle_input(event)
                

            self.ui.render()
            
            self.clock.tick(60)

        pygame.quit()

    def _run_simulation(self):
        
        self._setup_agents(agent_class=MirrorAgent)

        while self.running and not self.turn.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Get current player's agent and make a move
            agent = self.agents[self.turn.current_player.color]  #type: ignore
            piece = agent.choose_move(self.board)
            
            if piece:
                self.turn.place_piece(piece)
            else:
                self.turn.next_turn()
            
            self.ui.render()
            self.clock.tick(10) 
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.running = False

            self.ui.render()
            self.clock.tick(60)

        print(self.board.print_grid())
        self._save_stats()
        pygame.quit()

    def _save_stats(self):
        bits_per_cell = 3 if self.board.version else 2
        stats = {
            "timestamp": datetime.now().isoformat(),
            "board_version": "4-player" if self.board.version else "2-player",
            "final_scores": {str(color): score for color, score in self.turn.scores.items()},
            "winner": str(max(self.turn.scores, key=lambda color: self.turn.scores[color])),
            "board_state" : self.board_to_bitstring(self.board.print_grid().tolist(), bits_per_cell)
        }

        try: 
            with open("game_stats.json", "r") as f:
                all_stats = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError): 
            all_stats = []
        print(f"There are {len(all_stats)} games that have been recorded thus far. ")
        all_stats.append(stats)
        with open("game_stats.json", "w") as f:
            json.dump(all_stats, f, indent=2)
        
        print(f"Stats saved to game_stats.json")

    def _setup_agents(self, agent_class: type[RandomAgent | MirrorAgent]):
        self.agents = {}

        for player in self.turn.players:
            if agent_class == MirrorAgent:
                fallback = RandomAgent(player)
                self.agents[player.color] = MirrorAgent(player, fallback)
            else:
                self.agents[player.color] = agent_class(player)
    
    ### Helper Functions for storing board ###
    def board_to_bitstring(self, board, bits_per_cell):
        """Convert board to bitstring"""
        bits = ''
        for row in board:
            for cell in row:
                # Map color enum to integer, then to 2 bits
                bits += format(cell, f'0{bits_per_cell}b')
        return bits

    def bitstring_to_board(self, bitstring, size, bits_per_cell):
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