import unittest
from src.models import QuoridorGame

class TestNotation(unittest.TestCase):
    def test_notation_conversion(self):
        game = QuoridorGame()
        
        # Test e2 (Pawn Move)
        # e2 is (7, 4) in (r, c)
        # r=7 -> rank 9-7=2 -> '2'
        # c=4 -> 'e'
        self.assertEqual(game.coords_to_notation(7, 4), "e2")
        self.assertEqual(game.notation_to_coords("e2"), (7, 4))
        
        # Test e2h (Wall)
        self.assertEqual(game.coords_to_notation(7, 4, 'H'), "e2h")
        self.assertEqual(game.notation_to_coords("e2h"), (7, 4, 'H'))
        
        # Test v orientation
        self.assertEqual(game.coords_to_notation(0, 0, 'V'), "a9v")
        self.assertEqual(game.notation_to_coords("a9v"), (0, 0, 'V'))

    def test_game_history(self):
        game = QuoridorGame()
        
        # Move P1 to e2 (7, 4) -> start is (8, 4)
        game.move_pawn(7, 4) 
        # Move P2 to e8 (1, 4) -> start is (0, 4)
        game.move_pawn(1, 4)
        
        notation = game.get_game_notation()
        self.assertEqual(notation, "1. e2 e8")
        
        # Add a wall
        # P1 places wall at e3h (r=6, c=4)
        game.place_wall(6, 4, 'H')
        
        notation = game.get_game_notation()
        self.assertEqual(notation, "1. e2 e8 2. e3h")

    def test_load_game(self):
        game = QuoridorGame()
        game.load_from_notation("1. e2 e8 2. e3h")
        
        # Verify State
        self.assertEqual(game.players[0].r, 7) # e2
        self.assertEqual(game.players[0].c, 4)
        
        self.assertEqual(game.players[1].r, 1) # e8
        self.assertEqual(game.players[1].c, 4)
        
        self.assertIn((6, 4, 'H'), game.walls)
        self.assertEqual(game.players[0].walls_remaining, 9)

if __name__ == '__main__':
    unittest.main()
