import math
from copy import deepcopy  # deepcopy is allowed within the function

def group1(self, board, depth=3):
    # Minimax function to simulate turns
    def minimax(board, depth, is_maximizing):
        if depth == 0 or self.endGameCheck(board):  # Base case: Max depth or game end
            return self.evaluate(board)  # Assuming `evaluate` exists in `AlgoBot.py`
        
        possible_moves = self.getPossibleMoves(board)  # Use existing method
        
        if not possible_moves:  # If no moves are available, return a large negative score for maximizing
            return -math.inf if is_maximizing else math.inf
        
        if is_maximizing:
            max_eval = -math.inf
            for move in possible_moves:
                board_copy = deepcopy(board)
                self.move(move, move[2][0], board_copy)  # Use existing `move` method
                eval = minimax(board_copy, depth - 1, False)  # Recurse with opponent's move
                max_eval = max(max_eval, eval)
            return max_eval
        else:
            min_eval = math.inf
            for move in possible_moves:
                board_copy = deepcopy(board)
                self.move(move, move[2][0], board_copy)  # Use existing `move` method
                eval = minimax(board_copy, depth - 1, True)  # Recurse with agent's move
                min_eval = min(min_eval, eval)
            return min_eval

    # Check if the game has ended (e.g., no pieces left or no possible moves)
    if self.endGameCheck(board):  
        print("Game over detected in group1")
        self.game.end_turn()  # End the game or turn
        return None, None

    # Main logic of `group1`
    best_move = None
    best_score = -math.inf
    possible_moves = self.getPossibleMoves(board)

    if not possible_moves:  # Handle case where no moves are available
        print("No possible moves left, ending turn")
        self.game.end_turn()  # End the turn if no moves are possible
        return None, None

    # Evaluate all possible moves using Minimax
    for move in possible_moves:
        board_copy = deepcopy(board)  # Make a copy of the board for simulation
        self.move(move, move[2][0], board_copy)  # Simulate the move
        score = minimax(board_copy, depth - 1, False)  # Call Minimax for the opponent's turn

        if score > best_score:  # Track the best score and corresponding move
            best_score = score
            best_move = move

    # Return the best move found, or (None, None) if no valid move was found
    return (best_move, best_move[2][0]) if best_move else (None, None)
