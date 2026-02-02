# Blokus

Exploring the game of Blokus with Game Theory, Software Engineering, and a bit of AI.
This project was developed with PyGame and Python. Further advancements will include PyTorch, Scikit-learn, etc.

## Understanding the Game of Blokus

**Blokus** is a two to four player abstract strategy board game where players score points by occupying the board with their colored polyomino pieces.

The grid is **20×20 square grid** (400 total squares). The game includes **84 tiles**, made up of **21 unique shapes** in each of four colors: **blue, yellow, red, and green**.

### Tiles

- Each player has the same 21 shapes.
- The shapes are all possible **free polyominoes** made from 1 to 5 squares:
    - 1 monomino
    - 1 domino
    - 2 trominoes
    - 5 tetrominoes
    - 12 pentominoes

---

### Rules of Play

#### Turn Order

- Players take turns in the following color order: **Blue → Yellow → Red → Green**.

#### Placement Rules

- The **first tile** of each color must be placed in one of the **four board corners**.
- Every new tile must:
    - Touch **at least one tile of the same color at a corner**.
    - **Never touch tiles of the same color along an edge** (corner contact only).
- Tiles of **different colors may touch freely**, including edge-to-edge.

### Game Flow

- If a player cannot place any remaining tile, they are **skipped for the rest of the game**.
- The game ends when **no player can make a legal move**.

---

### Scoring

- Each unplayed square counts as **−1 point**.
    - Example: an unplayed tetromino scores −4 points.
- **Bonus points**:
    - +15 points for playing *all* tiles.
    - +5 additional points if the **last tile played is the monomino**.
- The player with the **highest total score** wins.
