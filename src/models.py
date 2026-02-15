import pygame
from .constants import *
from .pathfinding import is_path_exists

class Player:
    def __init__(self, start_pos, goal_row, color, walls):
        self.r, self.c = start_pos  # (row, col)
        self.goal_row = goal_row    # The row index they need to reach (0 or 8)
        self.color = color
        self.walls_remaining = walls

    def move(self, r, c):
        self.r = r
        self.c = c

    def has_won(self):
        return self.r == self.goal_row

class QuoridorGame:
    def __init__(self, num_players=2):
        self.num_players = num_players
        self.turn = 0  # 0 or 1 (for 2 players)
        
        # Initialize players
        # Player 1: Starts at (8, 4), Goal row 0 (Top)
        # Player 2: Starts at (0, 4), Goal row 8 (Bottom)
        self.players = [
            Player((8, 4), 0, RED, WALLS_PER_PLAYER_2),
            Player((0, 4), 8, BLUE, WALLS_PER_PLAYER_2)
        ]
        
        # Walls: Set of (r, c, orientation). 
        # r, c are 0..7 representing the top-left coordinate of the 2x2 block
        # orientation: 'H' or 'V'
        self.walls = set()
        
        # History for notation
        self.move_history = [] 

    def current_player(self):
        return self.players[self.turn]

    def switch_turn(self):
        self.turn = (self.turn + 1) % self.num_players

    def coords_to_notation(self, r, c, orientation=None):
        # Columns: a-i (0-8)
        # Rows: 1-9 (8-0). Note: board row 8 is '1', row 0 is '9' usually? 
        # Standard Quoridor:
        # Rows are 1-9 from bottom (row 8) to top (row 0).
        # So row_idx 8 -> '1', row_idx 0 -> '9'.
        # Formula: rank = 9 - r
        
        col_char = chr(ord('a') + c)
        rank = 9 - r
        
        base = f"{col_char}{rank}"
        
        if orientation:
            return f"{base}{orientation.lower()}"
            
        return base

    def notation_to_coords(self, not_str):
        # e2 -> (7, 4)
        # e2h -> (7, 4, 'H')
        
        not_str = not_str.lower().strip()
        if not not_str: return None
        
        col_char = not_str[0]
        c = ord(col_char) - ord('a')
        
        # Check for orientation
        orientation = None
        if not_str[-1] in ('h', 'v'):
            orientation = not_str[-1].upper()
            rank_str = not_str[1:-1]
        else:
            rank_str = not_str[1:]
            
        try:
            rank = int(rank_str)
        except:
            return None
            
        r = 9 - rank
        
        if orientation:
            return (r, c, orientation)
        return (r, c)

    def is_valid_wall_placement(self, r, c, orientation):
        """
        Validates wall placement:
        1. Bounds check (0 <= r, c <= 7)
        2. Collision with existing walls (Intersection and Overlap)
        3. Golden Rule: Both players must have a path to their goal.
        """
        if not (0 <= r < 8 and 0 <= c < 8):
            return False

        # Check collisions
        if (r, c, 'H') in self.walls or (r, c, 'V') in self.walls:
            return False  # Direct overlap or intersection
        
        if orientation == 'H':
            if (r, c - 1, 'H') in self.walls or (r, c + 1, 'H') in self.walls:
                return False
        else: # 'V'
            if (r - 1, c, 'V') in self.walls or (r + 1, c, 'V') in self.walls:
                return False

        # Golden Rule Check
        # Temporarily add wall
        self.walls.add((r, c, orientation))
        
        valid = True
        for p in self.players:
            # goal_nodes should be all cells in p.goal_row
            goals = [(p.goal_row, col) for col in range(9)]
            if not is_path_exists(self, (p.r, p.c), goals):
                valid = False
                break
        
        self.walls.remove((r, c, orientation))
        return valid

    def place_wall(self, r, c, orientation):
        if self.current_player().walls_remaining > 0 and self.is_valid_wall_placement(r, c, orientation):
            # Record move
            not_str = self.coords_to_notation(r, c, orientation)
            self.move_history.append(not_str)
            
            self.walls.add((r, c, orientation))
            self.current_player().walls_remaining -= 1
            self.switch_turn()
            return True
        return False

    def is_move_blocked(self, r1, c1, r2, c2):
        """
        Checks if a wall blocks the movement between (r1, c1) and (r2, c2).
        Assumes cells are adjacent.
        """
        # Determine direction
        if r1 == r2: # Horizontal movement
            # Moving between columns c1 and c2
            col_min = min(c1, c2)
            # Blocked if Vertical wall at (r1, col_min) or (r1-1, col_min)
            if (r1, col_min, 'V') in self.walls: return True
            if (r1 - 1, col_min, 'V') in self.walls: return True
        
        elif c1 == c2: # Vertical movement
             # Moving between rows r1 and r2
            row_min = min(r1, r2)
            # Blocked if Horizontal wall at (row_min, c1) or (row_min, c1-1)
            if (row_min, c1, 'H') in self.walls: return True
            if (row_min, c1 - 1, 'H') in self.walls: return True
            
        return False

    def get_valid_pawn_moves(self, player_idx=None, check_walls_only=False):
        """
        Returns a list of valid (r, c) moves for the current player (or specified player).
        check_walls_only: If True, ignores other pawns (used for BFS raw connectivity).
        """
        if player_idx is None:
            player_idx = self.turn
        
        player = self.players[player_idx]
        opponent = self.players[1 - player_idx]
        
        r, c = player.r, player.c
        moves = []
        
        # Directions: Up, Down, Left, Right
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            
            if 0 <= nr < 9 and 0 <= nc < 9:
                if not self.is_move_blocked(r, c, nr, nc):
                    if check_walls_only:
                        moves.append((nr, nc))
                    else:
                        # Check if occupied by opponent
                        if (nr, nc) == (opponent.r, opponent.c):
                            # Try to jump
                            jump_r, jump_c = nr + dr, nc + dc
                            
                            # Straight Jump
                            if 0 <= jump_r < 9 and 0 <= jump_c < 9 and not self.is_move_blocked(nr, nc, jump_r, jump_c):
                                moves.append((jump_r, jump_c))
                            else:
                                # Diagonal Jump (if blocked or edge)
                                # Try both diagonals from the opponent's position
                                # Relative to opponent (nr, nc), we try 90 degree turns
                                # dr, dc is the direction TO the opponent
                                # Diagonals are (nr + dc, nc + dr) and (nr - dc, nc - dr)
                                
                                diag1 = (nr + dc, nc + dr)
                                diag2 = (nr - dc, nc - dr)
                                
                                for dr_d, dc_d in [(dc, dr), (-dc, -dr)]:
                                    diag_r, diag_c = nr + dr_d, nc + dc_d
                                    if 0 <= diag_r < 9 and 0 <= diag_c < 9:
                                        if not self.is_move_blocked(nr, nc, diag_r, diag_c):
                                            moves.append((diag_r, diag_c))
                                            
                        else:
                            moves.append((nr, nc))
                            
        return moves

    # Helper for pathfinding to call
    def get_valid_moves(self, r, c, check_walls_only=True):
        """
        Used by BFS. Mimics the signature expected by BFS if we passed a 'board-like' object.
        But BFS calls board.get_valid_moves(x, y, ...).
        We'll adapt this. The BFS in pathfinding.py expects (x, y) which matches our (r, c) if consistent.
        """
        # Create a dummy player at (r,c) to reuse logic?
        # Actually logic inside get_valid_pawn_moves assumes checks relative to self.players[player_idx]
        # We need a generic "get neighbors" for BFS.
        
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 9 and 0 <= nc < 9:
                 if not self.is_move_blocked(r, c, nr, nc):
                     moves.append((nr, nc))
        return moves

    def move_pawn(self, r, c):
        if (r, c) in self.get_valid_pawn_moves():
            # Record move
            not_str = self.coords_to_notation(r, c)
            self.move_history.append(not_str)
            
            self.current_player().move(r, c)
            self.switch_turn()
            return True
        return False
        
    def get_game_notation(self):
        # Format: 1. e2 e8 2. e3 ...
        out = []
        for i in range(0, len(self.move_history), 2):
            move_num = (i // 2) + 1
            p1_move = self.move_history[i]
            p2_move = self.move_history[i+1] if i+1 < len(self.move_history) else ""
            out.append(f"{move_num}. {p1_move} {p2_move}")
        return " ".join(out).strip()
        
    def load_from_notation(self, notation_str):
        # Reset game
        self.__init__(self.num_players)
        
        # Parse tokens
        # Remove numbers and dots
        clean = notation_str.replace('.', ' ')
        tokens = clean.split()
        
        moves = []
        for t in tokens:
            if t.isdigit(): continue # Skip standalone numbers
            moves.append(t)
            
        # Replay
        for m in moves:
            coords = self.notation_to_coords(m)
            if not coords:
                print(f"Invalid move token: {m}")
                continue # or break/error
            
            if len(coords) == 3:
                r, c, o = coords
                # Force placement without validation? 
                # Ideally validation should pass if it's a valid game.
                # Use internal methods but ensure turn switching matches.
                # If we use place_wall, it checks validity and switches turn.
                if not self.place_wall(r, c, o):
                    print(f"Failed to replay wall: {m}")
                    return False
            else:
                r, c = coords
                if not self.move_pawn(r, c):
                     print(f"Failed to replay move: {m}")
                     return False
        return True
