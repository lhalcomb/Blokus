from utils.dsa import MaxHeap as mh
from engine.board import Board
from engine.piece import Piece

from agents.player import Player


def actions_from_state( board_state: Board, player: Player, ACTIONS_C: int) -> list[Piece]:  #type: ignore
        # #sees if a move can be placed, then returns the biggest pieces first
        possible_moves = mh(ACTIONS_C)
        seen = set()

        for shape in player.remaining_pieces: 
            piece = Piece(shape, player.color)
            for rotations, flipped in board_state.get_orientations(shape):
                piece.rotations = rotations
                piece.flipped = flipped

                offsets = piece.tiles()
                for val_diag in board_state.get_valid_diagonals(player.color):
                    fx, fy = val_diag % board_state.size, val_diag // board_state.size
                    for ox, oy in offsets:
                        piece.set_pos(fx - ox, fy - oy)
                        if board_state.can_place_piece(piece):
                            key = (shape, piece.x, piece.y, piece.rotations, piece.flipped)
                            if key not in seen: 
                                seen.add(key)
                                possible_moves.add((piece.size(), key))

        actions_ = possible_moves.getTop()
        return _populate_moves(actions_, player)

def _populate_moves(actions_, player: Player):
        moves = []

        for _, key in actions_:
            shape, x, y, rotations, flipped = key
            p = Piece(shape, player.color)
            p.set_pos(x, y)
            p.rotations = rotations
            p.flipped = flipped
            moves.append(p)

        return moves