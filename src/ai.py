import copy
import random
from .pathfinding import bfs, get_shortest_path

class QuoridorAI:
    def __init__(self, game, player_idx, depth=2):
        self.game = game
        self.player_idx = player_idx # The AI's index
        self.opponent_idx = 1 - player_idx
        self.depth = depth

    def get_best_move(self, game_state):
        print(f"AI Thinking... (Depth {self.depth})")
        _, best_move, move_type = self.minimax(game_state, self.depth, float('-inf'), float('inf'), True)
        return best_move, move_type

    def evaluate(self, game):
        # Heuristic: Opponent Path Length - AI Path Length
        ai_p = game.players[self.player_idx]
        op_p = game.players[self.opponent_idx]
        
        ai_goals = [(ai_p.goal_row, c) for c in range(9)]
        op_goals = [(op_p.goal_row, c) for c in range(9)]
        
        # We can use bfs (which delegates to a_star returning int)
        dist_ai = bfs(game, (ai_p.r, ai_p.c), ai_goals)
        dist_op = bfs(game, (op_p.r, op_p.c), op_goals)
        
        if dist_ai == float('inf'): dist_ai = 1000
        if dist_op == float('inf'): dist_op = 1000
        
        return dist_op - dist_ai

    def get_all_possible_moves(self, game, player_idx):
        moves = []
        
        # 1. Pawn Moves
        pawn_moves = game.get_valid_pawn_moves(player_idx)
        
        # Sort pawn moves?
        # Heuristic: Moves closer to goal row are better.
        goal_row = game.players[player_idx].goal_row
        pawn_moves.sort(key=lambda m: abs(m[0] - goal_row))
        
        for m in pawn_moves:
            moves.append(((m), 'MOVE'))
            
        # 2. Wall placements
        if game.players[player_idx].walls_remaining > 0:
            # OPTIMIZATION:
            # Instead of checking random neighbors, identifying "Critical Walls".
            # A critical wall is one that intersects the opponent's currently shortest path.
            
            op_p = game.players[1 - player_idx]
            op_goals = [(op_p.goal_row, c) for c in range(9)]
            op_path = get_shortest_path(game, (op_p.r, op_p.c), op_goals)
            
            candidates = set()
            
            # Add walls that block this path
            # Path is list of nodes [(r,c), (r,c)...]
            # Between node i and i+1, we can place a wall.
            if len(op_path) > 1:
                for i in range(len(op_path) - 1):
                    r1, c1 = op_path[i]
                    r2, c2 = op_path[i+1]
                    
                    # If moving Vertical (c1==c2), we need Horizontal wall
                    # Wall at (min(r1,r2), c1, 'H') or (min(r1,r2), c1-1, 'H')
                    if c1 == c2:
                        row = min(r1, r2)
                        candidates.add((row, c1, 'H'))
                        candidates.add((row, c1 - 1, 'H'))
                    # If moving Horizontal (r1==r2), we need Vertical wall
                    elif r1 == r2:
                        col = min(c1, c2)
                        candidates.add((r1, col, 'V'))
                        candidates.add((r1 - 1, col, 'V'))
                        
            # Also add some walls near self to defend/deflect?
            # Or just rely on raw search finding them if we add a few nearby walls.
            # Adding immediate neighbors of self just in case.
            my_p = game.players[player_idx]
            for dr in range(-1, 2):
                for dc in range(-1, 2):
                    candidates.add((my_p.r + dr, my_p.c + dc, 'H'))
                    candidates.add((my_p.r + dr, my_p.c + dc, 'V'))
            
            # Filter valid
            for r, c, orient in candidates:
                if game.is_valid_wall_placement(r, c, orient):
                     # Extra check: Don't place wall if it massively increases OUR path?
                     # Maybe too expensive to check every time.
                     moves.append(((r, c, orient), 'WALL'))
                            
        return moves

    def minimax(self, game, depth, alpha, beta, maximizing_player):
        if depth == 0 or game.players[0].has_won() or game.players[1].has_won():
            return self.evaluate(game), None, None

        current_player_idx = self.player_idx if maximizing_player else self.opponent_idx
        possible_moves = self.get_all_possible_moves(game, current_player_idx)
        
        # Don't shuffle if we want stable sorting, or shuffle only same-priority.
        # random.shuffle(possible_moves) 
        
        best_move = None
        best_type = None
        
        if maximizing_player:
            max_eval = float('-inf')
            for move_data, move_type in possible_moves:
                game_copy = copy.deepcopy(game)
                if move_type == 'MOVE':
                    game_copy.move_pawn(*move_data)
                else:
                    game_copy.place_wall(*move_data)
                
                eval_score, _, _ = self.minimax(game_copy, depth - 1, alpha, beta, False)
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move_data
                    best_type = move_type
                    
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval, best_move, best_type
        
        else:
            min_eval = float('inf')
            for move_data, move_type in possible_moves:
                game_copy = copy.deepcopy(game)
                if move_type == 'MOVE':
                    game_copy.move_pawn(*move_data)
                else:
                    game_copy.place_wall(*move_data)
                    
                eval_score, _, _ = self.minimax(game_copy, depth - 1, alpha, beta, True)
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move_data
                    best_type = move_type
                    
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval, best_move, best_type
