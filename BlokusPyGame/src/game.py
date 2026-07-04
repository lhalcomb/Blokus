import pygame

from analytics.save_games import SaveGame
from engine.board import Board
from engine.turn import Turn
from ui.ui import UI

from agents.mirror import MirrorAgent 
from agents.random import RandomAgent
from agents.minimax import MiniMaxAgent
from agents.mcts import MCTSAgent
from agents.markov_process import MPAgent


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

                self.ui.handle_input(event)
                

            self.ui.render()
            
            self.clock.tick(60)

        pygame.quit()
    
    def _run_player_vs_cpu(self):
        
        #self._setup_agents(agent_class=MiniMaxAgent)
        self._setup_agents(agent_class=MCTSAgent)
        while self.running:
            self.ui.render()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                current_player = self.turn.current_player
               
                
                if current_player == self.turn.players[0]:
                    self.ui.handle_input(event)
                else:
                    agent = self.agents[self.turn.current_player.color] #type: ignore
                    piece = agent.choose_move(self.board)
                    if piece:
                        self.turn.place_piece(piece)
                    else:
                        self.turn.next_turn()

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
        
        config_map = {
            "mirror_vs_mirror": MirrorAgent,
            "random_vs_random": RandomAgent,
            "mirror_vs_random": MirrorAgent, 
            "random_vs_minimax": MiniMaxAgent,
            "random_vs_mcts": MCTSAgent,
            "minimax_vs_mcts": MCTSAgent,
            "markov_vs_random": MPAgent
        }
        
        if self.agent_config not in config_map:
            raise ValueError(f"Unknown agent config: {self.agent_config}")
        
        self._setup_agents(agent_class=config_map[self.agent_config])

        while self.running and not self.turn.game_over:
            self.ui.render()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
        
            agent = self.agents[self.turn.current_player.color] #type: ignore
            piece = agent.choose_move(self.board)
            
            if piece:
                self.turn.place_piece(piece)
            else:
                self.turn.next_turn()
            
            
            self.clock.tick(30) 

        print(self.board.print_grid())
        bits_per_cell = 3 if self.board.version else 2
        stats = self.savegame.set_stats(bits_per_cell, self.board, self.turn)
        
        return stats
    
    def _setup_agents(self, agent_class: type[RandomAgent | MirrorAgent | MiniMaxAgent | MCTSAgent| MPAgent]):
        self.agents = {} #{<Color.PURPLE: 10566880>: <ai.RandomAgent object at 0x106ac4f50>, <Color.ORANGE: 14715964>: <ai.MiniMaxAgent object at 0x106ac4ce0>} for Random vs MiniMax
        players = list(self.turn.players)

        if agent_class == MirrorAgent:
            for player in players:
                fallback = RandomAgent(player)
                self.agents[player.color] = MirrorAgent(player, fallback)

        elif agent_class == RandomAgent:
            for player in players:
                self.agents[player.color] = RandomAgent(player)

        elif agent_class == MiniMaxAgent:
            player1, player2 = players[0], players[1]
            self.agents[player1.color] = RandomAgent(player1)
            self.agents[player2.color] = MiniMaxAgent(player2, player1)

        elif agent_class == MCTSAgent:
            # For minimax_vs_mcts config: player1 is MiniMax, player2 is MCTS
            player1, player2 = players[0], players[1]
            if self.agent_config == "minimax_vs_mcts":
                self.agents[player1.color] = MiniMaxAgent(player1, player2)
                self.agents[player2.color] = MCTSAgent(player2, player1)
            else:  # Both MCTS
                self.agents[player1.color] = MCTSAgent(player1, player2)
                self.agents[player2.color] = MCTSAgent(player2, player1)
        
        elif agent_class == MPAgent:
            from utils.color import Color
            players_by_color = {p.color: p for p in players}
            purple = players_by_color[Color.PURPLE]
            orange = players_by_color[Color.ORANGE]
            agent = MPAgent(purple, orange, self.turn)
            print("Running rollouts...")
            P, r = agent._build_transition_matrix(self.board)
            agent.Mk = agent._precompute_Mk(P, r, k=20) #type: ignore
            print(f"Done. States: {len(agent.state_idx)}")
            self.agents[Color.PURPLE] = agent
            self.agents[Color.ORANGE] = RandomAgent(orange)
