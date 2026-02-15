import pygame
import sys
from src.constants import *
from src.ui import QuoridorUI

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Quoridor - AI Agent Remake")
    
    clock = pygame.time.Clock()
    ui = QuoridorUI(screen)
    
    # Initialize AI for Player 2 (Blue)
    from src.ai import QuoridorAI
    # Try Depth 3 now with A* optimization
    ai = QuoridorAI(ui.game, player_idx=1, depth=4)
    
    running = True
    while running:
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Delegate all input to UI
            ui.handle_input(event)
            
        # Logic
        if ui.state == 'GAME':
            # Update AI reference to current game (in case of Load/Reset)
            if ai.game != ui.game:
                ai.game = ui.game

            # AI Turn
            if ui.game.turn == 1 and not ui.game.players[1].has_won() and not ui.game.players[0].has_won():
                # Process AI move
                pygame.display.set_caption("Quoridor - AI Thinking...")
                pygame.event.pump() 
                
                # Get move
                move_data, move_type = ai.get_best_move(ui.game)
                
                if move_type == 'MOVE':
                    ui.game.move_pawn(*move_data)
                elif move_type == 'WALL':
                    ui.game.place_wall(*move_data)
                
                ui.check_win()
                pygame.display.set_caption("Quoridor - AI Agent Remake")
        
        # Draw (delegates to draw_menu or draw_game internally)
        ui.draw()
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
