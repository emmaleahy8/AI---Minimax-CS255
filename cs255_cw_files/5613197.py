import random
import math

class Player:
	
	def __init__(self, name):
		self.name = name
		self.numExpanded = 0 # Use this to track the number of nodes you expand
		self.numPruned = 0 # Use this to track the number of times you prune 

	def getMove(self, gameBoard):
		self.numExpanded += 1 # Count root node

		depth = self._choose_depth(gameBoard) # Choose depth of search for this move

		# List of columns with legal moves ordered by distance from center (i.e. columns that are not full)
		movesList = self._ordered_moves(gameBoard, self.name)

		# If there are no legal moves (i.e. full board), return 0
		if len(movesList) == 0:
			return 0
		
		bestMove = movesList[0] # Intialise the best move seen so far
		bestScore = -float("inf") # Intialise the best score for our search at -inf so that any real score is larger

		# Try each legal move and evaluate it using minimax
		for col in movesList:
			# Simulate move by placing a piece in a valid column
			gameBoard.addPiece(col, self.name)

			# Opponent to play next, so isMaxPlayer = False - MIN layer
			score = self._minimax(gameBoard, depth - 1, False)

			# Undo the simulated move to restore the board before trying the next column
			gameBoard.removePiece(col)

			# Keep track of the maximum score and best move seen so far
			if score > bestScore:
				bestScore = score
				bestMove = col

		# Return the best choice found by Minimax
		return bestMove
	
	def getMoveAlphaBeta(self, gameBoard):
		self.numExpanded += 1 # Count root node

		depth = self._choose_depth(gameBoard) # Choose depth for this move

		# Initialise alpha and beta
		alpha = -float("inf")
		beta = float("inf")
	
		# List of columns with legal moves ordered by distance from center (i.e. columns that are not full)
		movesList = self._ordered_moves(gameBoard, self.name)

		# If there are no legal moves (i.e. full board), return 0
		if len(movesList) == 0:
			return 0
		
		bestMove = movesList[0] # Intialise the best move seen so far
		bestScore = -float("inf") # Intialise the best score for our search at -inf so that any real score is larger
		
		# Try each legal move and evaluate it using minimax with alpha-beta pruning
		for col in movesList:
			# Simulate move by placing a piece in a valid column
			gameBoard.addPiece(col, self.name)

			# Opponent to play next, so isMaxPlayer = False - MIN layer
			score = self._alphabeta(gameBoard, depth - 1, alpha, beta, False)

			# Undo the simulated move to restore the board before trying the next column
			gameBoard.removePiece(col)

			# Keep track of the maximum score seen so far
			if score > bestScore:
				bestScore = score
				bestMove = col

			# If there is a forced win, choose this
			if bestScore >= 1000000:
				break

			# Update alpha at the root
			if bestScore > alpha:
				alpha = bestScore
		
		return bestMove
	
	def _minimax(self, gameBoard, depth, isMaxPlayer):
		# Add this position to node expansion counter, as each call to minimax corresponds to expanding one node in the game tree
		self.numExpanded += 1
		
		# --- Terminal Checks ---

		# Terminal: last move is winning move
		if gameBoard.checkWin():
			winner = gameBoard.lastPlay[2] # Determine who played the winning move
			if winner == self.name:
				return 1000000 # Return a large positive number if Max won
			else:
				return -1000000 # Return a large negative number if Min won
					
		# Terminal: draw
		if gameBoard.checkFull():
			return 0
		
		# Depth limit reached: evaluate heuristically to determine position's value
		if depth == 0:
			return self._evaluate(gameBoard)
		
		# --- Recursive Minimax Search ---
		
		# Max layer: Max's turn, so aim is to maximise the score
		if isMaxPlayer:
			best = -float("inf") # Initialise to very large negative number so that any real score will be larger 

			for col in self._ordered_moves(gameBoard, self.name):
				gameBoard.addPiece(col, self.name)
				value = self._minimax(gameBoard, depth - 1, False) # Call minimax algorithm for Min's turn
				gameBoard.removePiece(col) # Undo move to restore game board

				# Keep track of the maximum score seen over all child positions
				if value > best:	
					best = value
			
			return best

		# Min layer: opponent's turn, so we assume they are aiming to minimise the score
		else:
			opp = self._opponent() # Determine the opponent's name
			best = float("inf") # Initialise to very large positive number so that any real score will be smaller 

			for col in self._ordered_moves(gameBoard, opp):
				gameBoard.addPiece(col, opp)
				value = self._minimax(gameBoard, depth - 1, True) # Call minimax algorithm for Max's turn
				gameBoard.removePiece(col)

				# Keep track of the minimum value seen over all child positions
				if value < best:
					best = value

			return best
	
	def _alphabeta(self, gameBoard, depth, alpha, beta, isMaxPlayer):
		self.numExpanded += 1

		# --- Terminal Checks --- (same as minimax without pruning)

		# Terminal: last move is winning move
		if gameBoard.checkWin():
			winner = gameBoard.lastPlay[2] # Determine who played the winning more
			if winner == self.name:
				return 1000000 # Return a large positive number if Max won
			else:
				return -1000000 # Return a large negative number if Min won
					
		# Terminal: draw
		if gameBoard.checkFull():
			return 0
		
		# Depth limit reached: evaluate heuristically to determine position's value
		if depth == 0:
			return self._evaluate(gameBoard)

		# --- Recursive Search ---

		# Max layer: Max's turn, so aim is to maximise the score
		if isMaxPlayer:
			value = -float("inf") 
			for col in self._ordered_moves(gameBoard, self.name):
				gameBoard.addPiece(col, self.name)
				value = max(value, self._alphabeta(gameBoard, depth - 1, alpha, beta, False))
				gameBoard.removePiece(col)

				alpha = max(alpha, value)

				# PRUNE
				if alpha >= beta:
					self.numPruned += 1
					break

			return value

		# Min layer: opponent's turn, so we assume they are aiming to minimise the score
		else:
			value = float("inf")
			opp = self._opponent()
			for col in self._ordered_moves(gameBoard, opp):
				gameBoard.addPiece(col, opp)
				value = min(value, self._alphabeta(gameBoard, depth - 1, alpha, beta, True))
				gameBoard.removePiece(col)

				beta = min(beta, value)

				# PRUNE
				if alpha >= beta:
					self.numPruned += 1
					break
			
			return value

	'''Heuristic Evaluation Function:
		Returns a score estimating how good the current position is for Max'''	
	def _evaluate(self, gameBoard):
		opp = self._opponent() 
		me = self.name
		n = gameBoard.winNum 
		score = 0 	# This will keep track of the score the evaluation function returns

		# --- Immediate Win/Loss Checks ---

		# If I can win right now, position is extremely good
		for col in self._legal_moves(gameBoard):
			gameBoard.addPiece(col, me)
			won = gameBoard.checkWin()
			gameBoard.removePiece(col)

			if won:
				return 1000000	# If there is a forced win, position is extremely good

		# If opponent can win right now, position is extremely bad
		for col in self._legal_moves(gameBoard):
			gameBoard.addPiece(col, opp)
			won = gameBoard.checkWin()
			gameBoard.removePiece(col)

			if won:
				return -1000000	# If there is a forced loss, position is extremely bad
		# --- Fork / immediate threats count ---
		# A tactical fork means the player has at least two immediate winning moves available next turn
		# This is dangerous because the opponent can only block one
		opp_wins = self._count_immediate_wins(gameBoard, opp)
		if opp_wins >= 2: 		# If opponent has fork, treat that as extremely bad - position is almost lost
			return -950000
		elif opp_wins == 1: 	# If opponent can create possible winning move for them next turn, treat it as bad
			score -= 120000

		my_wins = self._count_immediate_wins(gameBoard, me)
		if my_wins >= 2:		# If we have a fork, treat that as extremely good 
			return 800000
		elif my_wins == 1:
			score += 120000		# If we can create possible winning move for the next turn, treat this as good
		
		# --- Potential Fork Check ---
		if self._can_create_fork_next(gameBoard, opp):	# If the opponent can create a fork next turn, treat that as very bad (almost as bad as a forced loss)
			score -= 800000
		if self._can_create_fork_next(gameBoard, me):	# If we can create a fork next turn, treat that as good
			score += 100000

		# --- Window Scoring ---
		# Examine every possible contiguous line of length n (call it a window) to determine how good the board state is for me

		num_rows = gameBoard.numRows
		num_cols = gameBoard.numColumns

		# Directions of windows
		directions = [
			(1, 0), # vertical
			(0, 1), # horizontal
			(1, 1), # diagonal down-right
			(1, -1) # diagonal down-left
		]
		
		# Loop over every possible starting square for a window
		for row in range(num_rows):
			for col in range(num_cols):
				# Check if a window of length n fits on the board
				for (row_dir, col_dir) in directions:
					end_row = row + (n-1) * row_dir
					end_col = col + (n-1) * col_dir

					# If window would go off the board, ignore this start
					if end_row < 0 or end_row >= num_rows or end_col < 0 or end_col >= num_cols:
						continue

					# Initialise counters for this window 
					meCount = 0
					oppCount = 0
					empties = []

					# Iterate over each square in the window
					for k in range(n):
						# Compute coordinates of the k-th square
						r = row + k * row_dir
						c = col + k * col_dir
						v = gameBoard.checkSpace(r, c).value # See what is in the k-th square

						# Update counters
						if v == me:
							meCount += 1
						elif v == opp:
							oppCount += 1
						else:
							empties.append((r, c))
					
					score += self._score_window(gameBoard, meCount, oppCount, empties, n)

		return score
	
	# Counts the number of wins that a player can play next turn
	def _count_immediate_wins(self, gameBoard, player):
		wins = 0

		for col in self._legal_moves(gameBoard):
			gameBoard.addPiece(col, player)
			if gameBoard.checkWin():
				wins += 1
			gameBoard.removePiece(col)

		return wins

	# Generates list of columns player is legally allowed to play in at current game stage
	def _legal_moves(self, gameBoard):
		moves = []

		for c in range(gameBoard.numColumns):
			if gameBoard.colFills[c] < gameBoard.numRows: # A column is legal if it is not full (i.e. its fill count is less than the number of rows)
				moves.append(c)
	
		return moves
	
	''' Ordered Moves:
		Generates a list of legal moves ordered to improve alpha-beta pruning in the following order:
			Immediate winning moves 
			Blocking moves (prevent opponent's immediate win)
			Closest to centre '''
	def _ordered_moves(self, gameBoard, playerToMove):
		moves = self._legal_moves(gameBoard)
		center = (gameBoard.numColumns - 1) / 2.0
		opp = "O" if playerToMove == "X" else "X"

		scored = [] # list of tuples: (priority, distance from centre, column)

		for col in moves:
			priority = 2 # Default

			# Check for immediate win
			gameBoard.addPiece(col, playerToMove)
			if gameBoard.checkWin():
				priority = 0 # Highest priority
			gameBoard.removePiece(col)

			# If no immediate win, check if able to block immediate win for opponent
			if priority != 0:
				gameBoard.addPiece(col, opp)
				if gameBoard.checkWin():
					priority = 1 # High priority
				gameBoard.removePiece(col)

			distance = abs(col - center) # Distance from centre
			scored.append((priority, distance, col))

		scored.sort()
		return [col for (_, _, col) in scored]

	''' Determine name of opponent '''
	def _opponent(self):
		return "O" if self.name == "X" else "X"
	
	''' Determine score for given window'''
	def _score_window(self, gameBoard, meCount, oppCount, empties, n):

		# --- Blocked Window ---
		# Cannot win in a blocked window, as there are not enough available spaces to play
		if meCount > 0 and oppCount > 0:
			return 0
		
		# --- Empty Window ---
		# An empty window does not benefit me or the opponent
		if meCount == 0 and oppCount == 0:
			return 0
		
		# Is an empty square (r, c) playable next move?
		# It is playable if it is exactly the next empty row in that column
		def playable(r, c):
			return gameBoard.colFills[c] == r

		# --- My Window ---
		# A window with only X's and empty squares - beneficial to me
		if meCount > 0 and oppCount == 0:
			# The closer the window is to being filled with X's, the stronger the reward
			if meCount == n-1 and len(empties) == 1:
				(empty_r, empty_c) = empties[0]
				# Reward larger if we can play empty square next move
				return 5000 if playable(empty_r, empty_c) else 500
			
			# Otherwise scale up non-linearly 
			# 1 X -> 1, 2 X's -> 10, 3 X's -> 100, etc.
			return 10 ** (meCount - 1)
		
		# --- Opponent's Window ---
		# A window with only O's and empty squares - beneficial to opponent
		if oppCount > 0 and meCount == 0:
			# The closer the window is to being filled with O's, the larger the penalty
			if oppCount == n-1 and len(empties) == 1:
				(empty_r, empty_c) = empties[0]
				# Reward larger negative value if opponent can play empty square next move
				return -6000 if playable(empty_r, empty_c) else -600
			
			# Otherwise scale down non-linearly
			# 1 O -> -1, 2 O's -> -10, 3 O's -> -100
			return -(10 ** (oppCount - 1))

		return 0
	
	''' Determine what search depth to use for this turn.
		The more available moves, the shallower we will have to search for it to be feasible'''
	def _choose_depth(self, gameBoard):
		cells = gameBoard.numRows * gameBoard.numColumns

		# Count empty spaces
		empties = 0
		for c in range(gameBoard.numColumns):
			empties += (gameBoard.numRows - gameBoard.colFills[c])

		# The smaller the search, the greater the depth we are able to search without drastically increasing search time
		if cells <= 9: 	# 3x3 board
			d = 8
		elif cells <= 16: 	# 4x4
			d = 6
		elif cells <= 25: 	# about 5x5
			d = 5
		elif cells <= 36: 	# about 6x6
			d = 4
		else:
			d = 3
		
		# Never search deeper than remaining moves
		if d > empties:
			d = empties

		if d < 1:
			d = 1

		return d

	''' Determines whether a given player can create a fork next move'''
	def _can_create_fork_next(self, gameBoard, playerToMove):
		for col in self._legal_moves(gameBoard):
			gameBoard.addPiece(col, playerToMove)

			# There is a fork if the number of immediate wins is greater than 2
			if self._count_immediate_wins(gameBoard, playerToMove) >= 2:
				gameBoard.removePiece(col)
				return True
			
			gameBoard.removePiece(col)

		return False
