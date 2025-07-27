import random
from copy import deepcopy
import time

def group1(self, board):
    """
    Advanced checkers AI using minimax with alpha-beta pruning, 
    quiescence search, move ordering, and sophisticated evaluation
    """
    transposition_table = {}

    def order_moves(possible_moves):
        """Order moves for better alpha-beta pruning efficiency"""
        capture_moves = []
        king_moves = []
        center_moves = []
        spread_moves = []
        regular_moves = []

        for move in possible_moves:
            for choice in move[2]:
                piece_x, piece_y = move[0], move[1]
                dest_x, dest_y = choice

                # Prioritize captures (highest priority)
                if abs(dest_x - piece_x) > 1:
                    capture_moves.append((move, choice))
                # King promotion moves
                elif (self.color == (128, 128, 128) and dest_y == 0) or (self.color == (178, 102, 255) and dest_y == 7):
                    king_moves.append((move, choice))
                # Center control moves
                elif dest_x in [2, 3, 4, 5] and dest_y in [2, 3, 4, 5]:
                    center_moves.append((move, choice))
                else:
                    # Calculate spread value for positioning
                    distance_from_others = distance_to_other_pieces(board, dest_x, dest_y)
                    spread_moves.append((move, choice, distance_from_others))

        # Sort spread moves by distance (better positioning first)
        spread_moves = sorted(spread_moves, key=lambda x: -x[2])
        spread_moves = [(move, choice) for (move, choice, dist) in spread_moves]

        return capture_moves + king_moves + center_moves + spread_moves + regular_moves

    def distance_to_other_pieces(board, dest_x, dest_y):
        """Calculate average distance to other friendly pieces"""
        total_distance = 0
        piece_count = 0

        for i in range(8):
            for j in range(8):
                if (i, j) != (dest_x, dest_y):
                    square_piece = board.getSquare(i, j).squarePiece
                    if square_piece is not None and square_piece.color == self.color:
                        distance = abs(i - dest_x) + abs(j - dest_y)
                        total_distance += distance
                        piece_count += 1

        return total_distance / piece_count if piece_count > 0 else 0

    def quiescence_search(board, alpha, beta, maximizing_player, depth_limit=3):
        """Search only capture moves to avoid horizon effect"""
        if depth_limit == 0:
            return evaluate(board)

        stand_pat = evaluate(board)

        if maximizing_player:
            if stand_pat >= beta:
                return beta
            if alpha < stand_pat:
                alpha = stand_pat
        else:
            if stand_pat <= alpha:
                return alpha
            if beta > stand_pat:
                beta = stand_pat

        possible_moves = self.getPossibleMoves(board)
        # Only consider capture moves in quiescence search
        capture_moves = []
        for move in possible_moves:
            for choice in move[2]:
                if abs(choice[0] - move[0]) > 1:  # This is a capture
                    capture_moves.append((move, choice))

        for move, choice in capture_moves:
            simulated_board = deepcopy(board)
            self.moveOnBoard(simulated_board, move[:2], choice)

            eval_score = quiescence_search(simulated_board, alpha, beta, not maximizing_player, depth_limit - 1)
            
            if maximizing_player:
                if eval_score >= beta:
                    return beta
                alpha = max(alpha, eval_score)
            else:
                if eval_score <= alpha:
                    return alpha
                beta = min(beta, eval_score)

        return alpha if maximizing_player else beta

    def evaluate(board):
        """Comprehensive board evaluation function"""
        score = 0
        
        # Evaluation weights
        piece_value = 100
        king_value = 150
        mobility_weight = 10
        center_bonus = 20
        edge_penalty = -15
        king_safety_bonus = 25
        advancement_bonus = 5
        protection_bonus = 15
        threat_penalty = -20

        my_pieces = 0
        opponent_pieces = 0
        my_kings = 0
        opponent_kings = 0
        my_mobility = 0
        opponent_mobility = 0

        def is_protected(x, y, color, board):
            """Check if a piece is protected by friendly pieces"""
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < 8 and 0 <= ny < 8:
                    piece = board.getSquare(nx, ny).squarePiece
                    if piece and piece.color == color:
                        return True
            return False

        def is_threatened(x, y, color, board):
            """Check if a piece is under threat"""
            opponent_color = (178, 102, 255) if color == (128, 128, 128) else (128, 128, 128)
            
            for i in range(8):
                for j in range(8):
                    piece = board.getSquare(i, j).squarePiece
                    if piece and piece.color == opponent_color:
                        moves = board.get_valid_legal_moves(i, j)
                        for move in moves:
                            if abs(move[0] - i) > 1 and move == (x, y):  # Capture move targeting this piece
                                return True
            return False

        # Evaluate all pieces on the board
        for i in range(8):
            for j in range(8):
                square_piece = board.getSquare(i, j).squarePiece
                if square_piece is not None:
                    piece_score = 0
                    
                    if square_piece.color == self.color:
                        my_pieces += 1
                        
                        # Basic piece value
                        if square_piece.king:
                            my_kings += 1
                            piece_score += king_value
                            
                            # Kings should stay safe and central
                            if i in [1, 2, 5, 6] and j in [1, 2, 5, 6]:
                                piece_score += king_safety_bonus
                        else:
                            piece_score += piece_value
                            
                            # Advancement bonus for regular pieces
                            if self.color == (128, 128, 128):  # Grey pieces advance towards y=0
                                piece_score += advancement_bonus * (7 - j)
                            else:  # Purple pieces advance towards y=7
                                piece_score += advancement_bonus * j

                        # Center control bonus
                        if i in [2, 3, 4, 5] and j in [2, 3, 4, 5]:
                            piece_score += center_bonus

                        # Edge penalty
                        if i in [0, 7] or j in [0, 7]:
                            piece_score += edge_penalty

                        # Protection bonus
                        if is_protected(i, j, self.color, board):
                            piece_score += protection_bonus

                        # Threat penalty
                        if is_threatened(i, j, self.color, board):
                            piece_score += threat_penalty

                        # Calculate mobility
                        moves = board.get_valid_legal_moves(i, j)
                        my_mobility += len(moves)
                        
                        score += piece_score

                    else:  # Opponent piece
                        opponent_pieces += 1
                        
                        if square_piece.king:
                            opponent_kings += 1
                            piece_score -= king_value
                        else:
                            piece_score -= piece_value

                        # Calculate opponent mobility
                        moves = board.get_valid_legal_moves(i, j)
                        opponent_mobility += len(moves)
                        
                        score += piece_score

        # Mobility evaluation
        score += my_mobility * mobility_weight
        score -= opponent_mobility * mobility_weight

        # Material advantage bonus
        material_advantage = (my_pieces - opponent_pieces) * 50
        king_advantage = (my_kings - opponent_kings) * 25
        score += material_advantage + king_advantage

        # Endgame considerations
        total_pieces = my_pieces + opponent_pieces
        if total_pieces <= 8:  # Endgame
            # In endgame, prioritize piece activity and king centralization
            if my_kings > 0:
                score += my_mobility * 15  # Extra mobility bonus in endgame

        return score

    def minimax(board, depth, alpha, beta, maximizing_player):
        """Minimax algorithm with alpha-beta pruning and transposition table"""
        # Create a simple board state key for transposition table
        board_key = str([(i, j, board.getSquare(i, j).squarePiece.color if board.getSquare(i, j).squarePiece else None, 
                         board.getSquare(i, j).squarePiece.king if board.getSquare(i, j).squarePiece else None) 
                        for i in range(8) for j in range(8)])
        
        if board_key in transposition_table:
            return transposition_table[board_key]

        if depth == 0:
            eval_score = quiescence_search(board, alpha, beta, maximizing_player)
            transposition_table[board_key] = eval_score
            return eval_score

        possible_moves = self.getPossibleMoves(board)
        if not possible_moves:
            eval_score = evaluate(board)
            transposition_table[board_key] = eval_score
            return eval_score

        ordered_moves = order_moves(possible_moves)

        if maximizing_player:
            max_eval = float('-inf')
            for move, choice in ordered_moves:
                simulated_board = deepcopy(board)
                self.moveOnBoard(simulated_board, move[:2], choice)
                
                eval_score = minimax(simulated_board, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                
                if beta <= alpha:
                    break  # Alpha-beta pruning
            
            transposition_table[board_key] = max_eval
            return max_eval
        else:
            min_eval = float('inf')
            for move, choice in ordered_moves:
                simulated_board = deepcopy(board)
                self.moveOnBoard(simulated_board, move[:2], choice)
                
                eval_score = minimax(simulated_board, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                
                if beta <= alpha:
                    break  # Alpha-beta pruning
            
            transposition_table[board_key] = min_eval
            return min_eval

    # Main algorithm execution
    possible_moves = self.getPossibleMoves(board)
    if not possible_moves:
        return None, None

    best_move = None
    best_choice = None
    best_value = float('-inf')

    # Use iterative deepening for better move ordering and time management
    max_depth = min(self.depth, 6)  # Limit max depth to prevent excessive computation
    
    ordered_moves = order_moves(possible_moves)

    for move, choice in ordered_moves:
        simulated_board = deepcopy(board)
        self.moveOnBoard(simulated_board, move[:2], choice)
        
        move_value = minimax(simulated_board, max_depth - 1, float('-inf'), float('inf'), False)
        
        if move_value > best_value:
            best_value = move_value
            best_move = move
            best_choice = choice

    # Fallback to random move if no good move found
    if best_move is None:
        random_move = random.choice(possible_moves)
        best_choice = random.choice(random_move[2])
        best_move = random_move

    return best_move, best_choice
