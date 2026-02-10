# Blokus PyGame

1. [X] Game loop - initialized game loop
2. [X] Board display - got a basic board
3. [X] Pieces - defined all 21 piece shapes
4. [X] Piece transformations - implement rotate, flip, normalize
5. [X] Piece rendering - draw pieces on board visually
6. [X] Player class - track pieces, color, score, starting corner
7. [X] Mouse input - detect clicks, convert to board coordinates
8. [X] Piece selection UI - let player choose which piece to place
9. [X] Piece placement preview - show piece on hover before placement
10. [X] Core validation - implement can_place() logic:
    - [X] Bounds checking
    - [X] No overlap
    - [X] First move touches starting corner
    - [X] Corner-to-corner rule (same color)
    - [X] No edge-to-edge rule (same color)
11. [X] Place piece on board - update grid when valid placement
12. [X] Turn management - switch between players, skip if no valid moves
    - [X] Switch between players
    - [X] Skip if no valid moves
    - [X] Allow players to forfeit
13. [X] Valid move detection - check if player has any legal moves left
14. [ ] Game over logic - end game when all players blocked
15. [ ] Scoring - count remaining squares, determine winner
16. [ ] UI polish - show current player, remaining pieces, scores
17. [ ] Testing & debugging - validate all rules work correctly

# Blokus AI (Reinforcement Learning):

Will iron out after game logic done.

# Blokus Rules of Play: (From Wikipedia)

The standard rules of play for all variations of the game are as follows:

- Order of play is based on the color of pieces: blue, yellow, red, green.
- The first piece played of each color is placed in one of the board's four corners.
  Each new piece played must be placed so that it touches at least one piece of the same color by at least one corner — only
  corner-to-corner contact is allowed between pieces of the same color.
  On the other hand, there are no restrictions on how pieces of different colors touch each other.
- When a player cannot place a piece, they cannot play until the end of the game, and play continues for the other players.
  The game ends when no one can place any more pieces.
