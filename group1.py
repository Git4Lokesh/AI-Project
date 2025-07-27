import random
from copy import deepcopy
import time

def group1(self, board):
    transposition_table = {}

    def order_moves(possible_moves):
        capture_moves = []
        king_moves = []
        center_moves = []
        spread_moves = []
        regular_moves = []

        for move in possible_moves:
            for choice in move[2]:
                piece_x, piece_y = move[0], move[1]
                dest_x, dest_y = choice

                if abs(dest_x - piece_x) > 1:
                    capture_moves.append((move, choice))
                elif (self.color == 'GREY' and dest_y == 0) or (self.color == 'PURPLE' and dest_y == 7):
                    king_moves.append((move, choice))
                elif dest_x in [2, 3, 4, 5] and dest_y in [2, 3, 4, 5]:
                    center_moves.append((move, choice))
                else:
                    distance_from_others = distance_to_other_pieces(board, dest_x, dest_y)
                    spread_moves.append((move, choice, distance_from_others))

        spread_moves = sorted(spread_moves, key=lambda x: -x[2])
        spread_moves = [(move, choice) for (move, choice, dist) in spread_moves]

        return capture_moves + king_moves + center_moves + spread_moves + regular_moves

    def distance_to_other_pieces(board, dest_x, dest_y):
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
        if depth_limit == 0:
            return self.evaluate(board)

        stand_pat = self.evaluate(board)

        if stand_pat >= beta:
            return beta
        if alpha < stand_pat:
            alpha = stand_pat

        possible_moves = self.getPossibleMoves(board)
        capture_moves = [move for move in possible_moves if abs(move[2][0][0] - move[0]) > 1]

        for move in capture_moves:
            for choice in move[2]:
                simulated_board = deepcopy(board)
                self.moveOnBoard(simulated_board, move[:2], choice)

                if maximizing_player:
                    eval = quiescence_search(simulated_board, alpha, beta, False, depth_limit - 1)
                    if eval >= beta:
                        return beta
                    alpha = max(alpha, eval)
                else:
                    eval = quiescence_search(simulated_board, alpha, beta, True, depth_limit - 1)
                    if eval <= alpha:
                        return alpha
                    beta = min(beta, eval)

        return alpha if maximizing_player else beta

    def evaluate(board):
        score = 0
        capture_bonus = 10
        king_bonus = 50
        piece_bonus = 5
        mobility_weight = 3
        center_bonus = 5
        king_safety_bonus = 15
        spread_bonus = 10
        opponent_mobility_penalty = 2
        king_row_protection_bonus = 25

        my_pieces = 0
        opponent_pieces = 0
        my_kings = 0
        opponent_kings = 0
        my_mobility = 0
        opponent_mobility = 0
        my_capture_moves = 0
        opponent_capture_moves = 0
        piece_cluster_penalty = 0
        king_row_defenders = 0

        def has_protection(x, y, board):
            for i in range(max(0, x-1), min(8, x+2)):
                for j in range(max(0, y-1), min(8, y+2)):
                    if i == x and j == y:
                        continue
                    square_piece = board.getSquare(i, j).squarePiece
                    if square_piece is not None and square_piece.color == self.color:
                        return True
            return False

        for i in range(8):
            for j in range(8):
                square_piece = board.getSquare(i, j).squarePiece
                if square_piece is not None:
                    if square_piece.color == self.color:
                        my_pieces += 1
                        if square_piece.king:
                            my_kings += 1
                            score += king_bonus
                            if j in [0, 7]:
                                score -= king_safety_bonus
                        else:
                            score += piece_bonus

                        if i in [2, 3, 4, 5] and j in [2, 3, 4, 5]:
                            score += center_bonus

                        cluster_penalty = 1 / distance_to_other_pieces(board, i, j)
                        piece_cluster_penalty += cluster_penalty

                        if not has_protection(i, j, board):
                            score -= 10

                        if (self.color == 'GREY' and j == 7) or (self.color == 'PURPLE' and j == 0):
                            king_row_defenders += 1
                            if king_row_defenders >= 2:
                                score += king_row_protection_bonus