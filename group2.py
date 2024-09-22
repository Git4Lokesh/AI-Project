import random

# You need to complete this funtion which should return moves and choice 
# You can use the helper functions provided in the AlgoBot.py file
def group2(self,board):
    possible_moves = self.getPossibleMoves(board)
    if possible_moves == []:    
        self.game.end_turn()
        return
    random_move = random.choice(possible_moves)
    rand_choice = random.choice(random_move[2])   
    return random_move, rand_choice
