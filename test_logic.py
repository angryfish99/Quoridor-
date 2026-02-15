import sys
import os

# Ensure we can import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.models import QuoridorGame

def run_tests():
    print("=== Starting Logic Tests ===")
    game = QuoridorGame()
    
    # 1. Test Initial State
    p1 = game.players[0] # Red (Bottom-ish/Start 8,4 -> Goal 0)
    p2 = game.players[1] # Blue (Top-ish/Start 0,4 -> Goal 8)
    
    assert p1.r == 8 and p1.c == 4, "P1 start pos incorrect"
    assert p2.r == 0 and p2.c == 4, "P2 start pos incorrect"
    print("[PASS] Initial State")

    # 2. Test Basic Movement
    # Player 1 is Red, starts at (8, 4), turn 0
    valid_moves = game.get_valid_pawn_moves()
    # Should be (8, 3), (8, 5), (7, 4)
    # (9,4) is out of bounds
    expected = {(8, 3), (8, 5), (7, 4)}
    assert set(valid_moves) == expected, f"P1 moves incorrect: {valid_moves}"
    print("[PASS] Basic Movement Generation")
    
    # Move P1 to (7, 4)
    success = game.move_pawn(7, 4)
    assert success, "Move failed"
    assert game.players[0].r == 7, "P1 did not move"
    assert game.turn == 1, "Turn did not switch"
    print("[PASS] Move Execution & Turn Switch")

    # 3. Test Wall Placement (Simple)
    # P2's turn. Place wall at (7, 4, 'H') - should block P1 from moving back to (8,4)?
    # Wait, wall at (r,c) 'H' is between row r and r+1?
    # Logic in is_move_blocked:
    # Horizontal move blocked if V wall at ... 
    # Vertical move blocked if H wall at ...
    
    # Let's place a Horizontal wall at (6, 4).
    # This occupies (6,4) and (6,5).
    # It checks blocking between row 6 and 7?
    # In `is_move_blocked`: if Vertical movement (c1==c2), row_min = min(r1, r2).
    # Blocked if (row_min, c1, 'H') in walls.
    # So to block P1 at (7,4) from moving to (6,4), we need wall at (6, 4, 'H').
    
    success = game.place_wall(6, 4, 'H')
    assert success, "Wall placement failed"
    assert (6, 4, 'H') in game.walls, "Wall not in set"
    assert game.turn == 0, "Turn did not switch back to P1"
    
    # Now P1 (at 7,4) tries to move to (6,4). Should be blocked.
    assert game.is_move_blocked(7, 4, 6, 4), "Move should be blocked by wall"
    valid_moves_p1 = game.get_valid_pawn_moves()
    assert (6, 4) not in valid_moves_p1, f"P1 should not be able to move to (6,4). Moves: {valid_moves_p1}"
    print("[PASS] Wall Placement & Blocking")

    # 4. Test The Jump
    # Reset game for jump test
    game = QuoridorGame()
    # Set up adjacent pawns
    game.players[0].r, game.players[0].c = 4, 4
    game.players[1].r, game.players[1].c = 3, 4
    game.turn = 0 # P1's turn
    
    # P1 at (4,4), P2 at (3,4). P1 should be able to jump to (2, 4)
    moves = game.get_valid_pawn_moves()
    assert (2, 4) in moves, f"Jump move (2,4) missing. Moves: {moves}"
    print("[PASS] Straight Jump")
    
    # 5. Test Diagonal Jump (when blocked)
    # Place wall behind P2 at (2, 4, 'H') -> blocks P2(3,4) <-> (2,4)
    # Actually wall at (2,4,'H') blocks movement between row 2 and 3.
    game.walls.add((2, 4, 'H'))
    
    # Now P1 at (4,4), P2 at (3,4). Jump to (2,4) is blocked.
    # Should perform diagonal jump to (3,3) and (3,5) relative to board? 
    # Logic: "Relative to opponent (3,4)... Diagonals are (nr + dc, nc + dr)..."
    # P1 (4,4) -> P2 (3,4). Direction is (-1, 0).
    # Diagonals: (3 + 0, 4 + (-1)) = (3, 3)
    #            (3 - 0, 4 - (-1)) = (3, 5)
    moves = game.get_valid_pawn_moves()
    assert (2, 4) not in moves, "Blocked jump should not be valid"
    assert (3, 3) in moves, "Diagonal jump Left missing"
    assert (3, 5) in moves, "Diagonal jump Right missing"
    print("[PASS] Diagonal Jump")

    # 6. Test Golden Rule (Blocking all paths)
    game = QuoridorGame()
    game.turn = 1 # P2 turn
    # Trap P1 (8,4).
    # Walls surrounding P1:
    # (8, 4, 'V') blocks right? No, (8,4) is cell center.
    # To block (8,4)<->(8,5) we need V wall at (8, 4) or (7, 4)?
    # is_move_blocked: horizontal move c1..c2. col_min=4. 
    # Blocked if (r, 4, 'V').
    
    # Let's just try to place a wall that clearly blocks the only path.
    # Simpler scenario:
    # P1 at (8,4). P2 places walls to cage P1.
    # This is hard to script manually quickly, but let's test a simple known block.
    # If P1 is at (8,0) and walls cage it.
    
    game.players[0].r, game.players[0].c = 8, 0
    # Add walls around (8,0)
    # Wall above: H at (7, 0) -> blocks (8,0)-(7,0)
    game.walls.add((7, 0, 'H'))
    # Wall right: V at (8, 0) -> blocks (8,0)-(8,1)
    # Wait, (8,0) wall V:
    # is_move_blocked((8,0), (8,1)) -> col_min 0. Checks (8,0,'V').
    
    # We want to test placing the FINAL wall that seals the coffin.
    # Suppose we have H wall at (7,0).
    # We try to place V wall at (8,0).
    # BUT we need to make sure P1 has NO other way out.
    # P1 can't go left (edge), can't go down (edge).
    # Can go Up (blocked by 7,0 H).
    # Can go Right.
    # If we block Right, P1 is stuck.
    
    # So, game already has (7, 0, 'H').
    # Try to place (8, 0, 'V').
    # BFS should find NO path for P1.
    # So valid should be False.
    
    is_valid = game.is_valid_wall_placement(8, 0, 'V')
    assert not is_valid, "Should verify Golden Rule (prevent blocking last path)"
    print("[PASS] Golden Rule Validation")
    
    print("=== All Logic Tests Passed ===")

if __name__ == "__main__":
    run_tests()
