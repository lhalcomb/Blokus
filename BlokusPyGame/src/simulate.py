from ai import *
from color import Color
from turn import Turn
from board import Board


class SimulateGamePlay: 
    def __init__(self, num_simulations: int, version: bool, agents: dict[Color, RandomAgent | MirrorAgent]):
        self.num_simulations = num_simulations
        self.version = version
        self.agents = {}

        self.results = {
            'ties': 0,
            'winners': {}, #{Color: count}
            'scores_history': [] #list of final scores from each game
        }

    def run_simulations(self):
        """Run N games and collect stats"""

        for _ in range(self.num_simulations):
            final_scores = self._simulate_single_game()
            self.results['scores_history'].append(final_scores)
            self._check_for_tie(final_scores)

    def _simulate_single_game(self) -> dict:
        """Simulate a single game"""
        board = Board(self.version)
        turn = Turn(board)
        while not turn.game_over:
            agent = self.agents.get(turn.current_player.color) #type: ignore
            if agent:
                piece = agent.choose_move(board)
            
            if piece:
                turn.place_piece(piece)
            else:
                turn.next_turn()

        return turn.scores

    def _check_for_tie(self, scores: dict): 
        
        #collect winners from one game
        max_score = max(scores.values())
        winners = [color for color, score in scores.items() if score == max_score]

        #if there is more than one winner, theres a tie! otherwise, up the winners column
        if len(winners) > 1:
            self.results['ties'] += 1
        else:  #record the color that won as winner
            winner = winners[0]
            self.results['winners'][winner] = self.results['winners'].get(winner, 0) + 1

    def print_stats(self):
        """Print summary of all simulations"""
        print(f"Total games: {self.num_simulations}")
        print(f"Ties: {self.results['ties']}")
        print(f"Winners: {self.results['winners']}")