import pygame

from save_games import SaveGame
from board import Board
from turn import Turn
from ui import UI
from ai import *


class Game:
    def __init__(self, width: int, height: int, version: bool, simulate: bool,  play_ai: bool = False, num_simulations: int = 5, agent_config: str = "mirror_vs_mirror"):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption('Blokus')

        self.play_ai = play_ai
        self.simulate = simulate
        self.num_simulations = num_simulations
        if self.simulate:
            self.savegame = SaveGame(agent_config)

        self.clock = pygame.time.Clock()
        self.running = True
        self.board = Board(version)
        self.turn = Turn(self.board)
        self.ui = UI(pygame.display.set_mode((width, height)), self.board, self.turn)

        self.agent_config = agent_config
        if agent_config is None and version:
            raise ValueError("agent_config is only specified for Blokus Duo")
        

    def run(self):
        if self.simulate:
            self._run_simulations()
        elif self.play_ai:
            self._run_player_vs_cpu()
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
    
    def _run_player_vs_cpu(self):
        
        self._setup_agents(agent_class=MiniMaxAgent)
        while self.running and not self.turn.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                current_player = self.turn.current_player
                agent = self.agents[self.turn.current_player.color] #type: ignore
                

                if current_player == self.turn.players[0]:
                    self.ui.handle_input(event)
                else:
                    piece = agent.choose_move(self.board)
                    if piece:
                        self.turn.place_piece(piece)
                    else:
                        self.turn.next_turn()
            
            self.ui.render()
            self.clock.tick(30) 
        
        pygame.quit()


    def _run_simulations(self):
        all_stats = []
        for _ in range(self.num_simulations):
            self.board = Board(self.board.version)
            self.turn = Turn(self.board)
            self.ui.board = self.board
            self.ui.turn = self.turn
        
            game_stats = self._run_simulation()
            all_stats.append(game_stats)

        pygame.quit()
        self.savegame.save_stats(all_stats)
        self.savegame.count_wins_ties()

    def _run_simulation(self):
        
        configs = ["mirror_vs_mirror", "random_vs_random", "mirror_vs_random", "random_vs_minimax"] #option 3 doesn't exist rn
        
        if self.agent_config == configs[0]:
            self._setup_agents(agent_class=MirrorAgent)
        elif self.agent_config == configs[1]:
            self._setup_agents(agent_class=RandomAgent)
        elif self.agent_config == configs[3]:
            self._setup_agents(agent_class=MiniMaxAgent)

        while self.running and not self.turn.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
        
            agent = self.agents[self.turn.current_player.color] #type: ignore
            piece = agent.choose_move(self.board)

            if piece:
                self.turn.place_piece(piece)
            else:
                self.turn.next_turn()
            
            self.ui.render()
            self.clock.tick(30) 

        print(self.board.print_grid())
        bits_per_cell = 3 if self.board.version else 2
        stats = self.savegame.set_stats(bits_per_cell, self.board, self.turn)
        

        return stats
    
    def _setup_agents(self, agent_class: type[RandomAgent | MirrorAgent | MiniMaxAgent]):
        self.agents = {} #{<Color.PURPLE: 10566880>: <ai.RandomAgent object at 0x106ac4f50>, <Color.ORANGE: 14715964>: <ai.MiniMaxAgent object at 0x106ac4ce0>} for Random vs MiniMax

        for player in self.turn.players:
            if agent_class == MirrorAgent:
                fallback = RandomAgent(player)
                self.agents[player.color] = MirrorAgent(player, fallback)
            elif agent_class == RandomAgent:
                self.agents[player.color] = RandomAgent(player)
            elif agent_class == MiniMaxAgent:
                players = list(self.turn.players)
                random, opponent = players[0], players[1]
                self.agents[players[0].color] = RandomAgent(random)
                self.agents[players[1].color] = MiniMaxAgent(opponent, random)