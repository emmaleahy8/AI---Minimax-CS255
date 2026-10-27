# Adversarial Search for Connect

An implementation and evaluation of the Minimax algorithm, with and without alpha-beta pruning, applied to the game of Connect. This was my coursework for CS255 Artificial Intelligence at the University of Warwick.

Connect is a generalised version of Connect 4: two players take turns dropping pieces into the columns of a board, pieces fall to the lowest empty row under gravity, and the first player to form an uninterrupted line of a given length — horizontal, vertical or diagonal — wins. Unlike Connect 4, the board dimensions and the number of pieces needed to win are both varied, so the algorithm has to cope with a range of game configurations.

## What I implemented

Two adversarial search players, both written in Python 3 with no external imports:

- **Minimax without pruning** (`getMove()`) — searches the game tree to a fixed depth, using an evaluation function to score non-terminal positions.
- **Minimax with alpha-beta pruning** (`getMoveAlphaBeta()`) — the same search, but cutting off branches that cannot affect the final decision.

Both track the number of nodes expanded (`numExpanded`) and, for the pruning version, the number of branches pruned (`numPruned`), which are the main metrics used in the evaluation. My Minimax also supports adaptive depth selection, though that wasn't the focus of the evaluation.

## Evaluation

The report evaluates both algorithms on the Connect game across varying board sizes, search depths and win conditions. Performance is measured by nodes expanded, branches pruned, time taken and game outcomes. Unless stated otherwise, all experiments were run against a random player with fixed random seeds, using identical evaluation functions and move ordering for both algorithms so the comparison is fair.

The main findings:

- **Alpha-beta pruning expands far fewer nodes for equivalent outcomes.** Across boards from 5×6 to 6×8, pruning reduced the number of nodes expanded by 85–92%, while producing the same game results. Pruning changes the cost of the search, not the quality of the decisions.
- **The benefit grows with board size and search depth.** Without pruning, the search space grows rapidly as the branching factor increases, and Minimax becomes computationally infeasible on larger boards. Pruning reduces the effective branching factor, so its cost grows much more slowly with depth.
- **Pruning also makes performance more predictable.** The standard deviation of nodes expanded rises sharply with board size for plain Minimax; alpha-beta pruning reduced that variability by 74–87% on the 5×6 to 6×8 boards, giving more consistent runtimes across games.
- **The effect holds as the win condition changes.** Increasing the number of pieces needed to win lengthens games and enlarges the tree Minimax explores. On a 6-wide board at a fixed depth, across win conditions from 3 to 6 in a row, pruning kept the mean nodes expanded 79–99% lower than without pruning.
- **The per-node overhead is small.** Alpha-beta pruning costs marginally more per node (maintaining the alpha and beta bounds, move ordering), but this is dominated by the large reduction in the number of nodes expanded, so overall runtime is much lower.

Overall, alpha-beta pruning does not improve the quality of the decisions Minimax makes — the outcomes are equally effective — but it makes the algorithm substantially more scalable and feasible on larger, more complex game configurations.

## Running it

The game and board are provided; my code is in the player file. Requires Python 3.

```bash
python3 runGame.py
```

`runGame.py` creates a Connect environment and runs a game. The board size, win condition, and whether to use alpha-beta pruning are set there. A coarse measure of runtime can be taken with `time python3 runGame.py`.

## Project structure

```
player.py        # my solution: getMove() and getMoveAlphaBeta()  — the files below are provided
board.py         # Board class: game state and helper queries
game.py          # Game class: runs a game between two players
runGame.py       # sets up the environment and starts a game
randomPlayer.py  # a baseline player that picks a random non-full column
report.pdf       # the evaluation report
```

## Academic integrity

This was assessed coursework. If you're currently taking CS255 or a similar module, please don't copy it.
