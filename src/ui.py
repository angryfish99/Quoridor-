import pygame
import tkinter as tk # For clipboard
from .constants import *
from .models import QuoridorGame

class QuoridorUI:
    def __init__(self, screen):
        self.screen = screen
        self.game = QuoridorGame()
        self.font = pygame.font.SysFont(None, 36)
        self.large_font = pygame.font.SysFont(None, 72)
        
        # UI State
        self.state = 'MENU' # 'MENU' or 'GAME'
        self.selected_action = 'MOVE' # 'MOVE' or 'WALL'
        self.wall_orientation = 'H'   # 'H' or 'V'
        
        # Load Assets
        self.load_assets()

    def load_assets(self):
        # Wood Texture
        try:
            wood_img = pygame.image.load("assets/wood_texture.jpg").convert()
            self.tile_texture = pygame.transform.scale(wood_img, (CELL_SIZE, CELL_SIZE))
        except Exception as e:
            print(f"Failed to load wood texture: {e}")
            # Fallback to procedural
            self.tile_texture = self.create_wood_texture(CELL_SIZE, CELL_SIZE)
            
        # Pawn
        try:
            self.pawn_img = pygame.image.load("assets/pawn.png").convert_alpha()
            self.pawn_img = pygame.transform.smoothscale(self.pawn_img, (int(CELL_SIZE*0.8), int(CELL_SIZE*0.8)))
        except Exception as e:
            print(f"Failed to load pawn image: {e}")
            self.pawn_img = None

    def create_wood_texture(self, width, height):
        # Create a surface fallback
        s = pygame.Surface((width, height))
        s.fill((139, 69, 19))
        return s
        
    def draw(self):
        if self.state == 'MENU':
            self.draw_menu()
        else:
            self.draw_game()

    def draw_menu(self):
        self.screen.fill(BG_COLOR)
        
        title = self.large_font.render("QUORIDOR", True, GOLD)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Buttons
        # Simple text buttons for now
        opts = ["PLAY", "COPY GAME", "LOAD GAME"]
        
        mouse_pos = pygame.mouse.get_pos()
        
        start_y = 250
        for i, opt in enumerate(opts):
            color = WHITE
            # Highlight if hover
            rect = pygame.Rect(SCREEN_WIDTH//2 - 100, start_y + i*60, 200, 50)
            if rect.collidepoint(mouse_pos):
                color = GOLD
                
            txt = self.font.render(opt, True, color)
            txt_rect = txt.get_rect(center=rect.center)
            
            # Draw button background (optional)
            pygame.draw.rect(self.screen, (50, 50, 50), rect, border_radius=10)
            pygame.draw.rect(self.screen, color, rect, 2, border_radius=10)
            
            self.screen.blit(txt, txt_rect)

    def handle_menu_click(self, pos):
        # Check button clicks
        # Hardcoded rects for simplicity, matching draw_menu
        opts = ["PLAY", "COPY GAME", "LOAD GAME"]
        start_y = 250
        
        for i, opt in enumerate(opts):
            rect = pygame.Rect(SCREEN_WIDTH//2 - 100, start_y + i*60, 200, 50)
            if rect.collidepoint(pos):
                if i == 0: # PLAY
                    self.state = 'GAME'
                    # self.game = QuoridorGame() # Reset? Or continue? Maybe 'RESUME' / 'NEW GAME' split later.
                    # For now, let's just enter game. If user wants new game, they can restart app or we add "RESET"
                elif i == 1: # COPY
                    self.copy_game_to_clipboard()
                elif i == 2: # LOAD
                    self.load_game_from_clipboard()

    def copy_game_to_clipboard(self):
        notation = self.game.get_game_notation()
        try:
            r = tk.Tk()
            r.withdraw()
            r.clipboard_clear()
            r.clipboard_append(notation)
            r.update() # Stay open long enough to copy?
            r.destroy()
            print("Game copied to clipboard!")
        except Exception as e:
            print(f"Clipboard Error: {e}")

    def load_game_from_clipboard(self):
        try:
            r = tk.Tk()
            r.withdraw()
            content = r.clipboard_get()
            r.destroy()
            
            if content:
                print(f"Loading: {content}")
                success = self.game.load_from_notation(content)
                if success:
                    print("Game Loaded Successfully!")
                    self.state = 'GAME'
                else:
                    print("Failed to load game (invalid notation?)")
        except Exception as e:
             print(f"Clipboard Read Error: {e}")

    def draw_game(self):
        self.screen.fill(BG_COLOR)
        self.draw_board()
        self.draw_walls()
        self.draw_players()
        self.draw_hud()
        
        # Draw previews based on mouse position
        mx, my = pygame.mouse.get_pos()
        if self.is_mouse_on_board(mx, my):
            r, c, exact = self.get_board_coords(mx, my)
            # Only draw preview if valid coords
            if 0 <= r < 9 and 0 <= c < 9:
                if self.selected_action == 'MOVE':
                    # Only highlight if it's your turn? Or always?
                    # Always showing valid moves is nice.
                    self.draw_move_preview(r, c)
                elif self.selected_action == 'WALL':
                    self.draw_wall_preview(r, c)
                
    def draw_board(self):
        # Draw the grid squares
        for r in range(9):
            for c in range(9):
                x = BOARD_OFFSET_X + c * (CELL_SIZE + MARGIN)
                y = BOARD_OFFSET_Y + r * (CELL_SIZE + MARGIN)
                
                # Blit cached texture
                self.screen.blit(self.tile_texture, (x, y))
                
    def draw_players(self):
        for p in self.game.players:
            cx = BOARD_OFFSET_X + p.c * (CELL_SIZE + MARGIN) + CELL_SIZE // 2
            cy = BOARD_OFFSET_Y + p.r * (CELL_SIZE + MARGIN) + CELL_SIZE // 2
            
            if self.pawn_img:
                # Tint the pawn
                tinted = self.pawn_img.copy()
                tinted.fill(p.color, special_flags=pygame.BLEND_MULT)
                
                # Center it
                rect = tinted.get_rect(center=(cx, cy))
                self.screen.blit(tinted, rect)
            else:
                # Fallback circle
                pygame.draw.circle(self.screen, p.color, (cx, cy), CELL_SIZE // 3)
            
            # Draw highlight for current player
            if p == self.game.current_player():
                 pygame.draw.circle(self.screen, WHITE, (cx, cy), CELL_SIZE // 2, 2)
                 
    def draw_walls(self):
        for (r, c, orient) in self.game.walls:
            self.draw_single_wall(r, c, orient, color=GOLD)
            
    def draw_single_wall(self, r, c, orient, color):
        x = BOARD_OFFSET_X + c * (CELL_SIZE + MARGIN)
        y = BOARD_OFFSET_Y + r * (CELL_SIZE + MARGIN)
        
        if orient == 'H':
            wx = x
            wy = y + CELL_SIZE
            w_width = 2 * CELL_SIZE + MARGIN
            w_height = MARGIN
            pygame.draw.rect(self.screen, color, (wx, wy, w_width, w_height))
            
        else: # 'V'
            wx = x + CELL_SIZE
            wy = y
            w_width = MARGIN
            w_height = 2 * CELL_SIZE + MARGIN
            pygame.draw.rect(self.screen, color, (wx, wy, w_width, w_height))

    def draw_move_preview(self, r, c):
        # Highlight cell if it's a valid move
        valid_moves = self.game.get_valid_pawn_moves()
        if (r, c) in valid_moves:
             rect = pygame.Rect(
                    BOARD_OFFSET_X + c * (CELL_SIZE + MARGIN),
                    BOARD_OFFSET_Y + r * (CELL_SIZE + MARGIN),
                    CELL_SIZE, CELL_SIZE
                )
             s = pygame.Surface((CELL_SIZE, CELL_SIZE))
             s.set_alpha(128)
             s.fill(GREEN)
             self.screen.blit(s, (rect.x, rect.y))
             
             # Also assume click moves here
             # But we handle click in handle_click

    def draw_wall_preview(self, r, c):
        # Draw semi-transparent wall
        # Only if valid coords for wall (0-7)
        if not (0 <= r < 8 and 0 <= c < 8): return

        if self.game.is_valid_wall_placement(r, c, self.wall_orientation):
            color = (255, 215, 0, 128) # Gold transparent
            
            x = BOARD_OFFSET_X + c * (CELL_SIZE + MARGIN)
            y = BOARD_OFFSET_Y + r * (CELL_SIZE + MARGIN)
            
            if self.wall_orientation == 'H':
                w_width = 2 * CELL_SIZE + MARGIN
                w_height = MARGIN
                wx, wy = x, y + CELL_SIZE
            else:
                w_width = MARGIN
                w_height = 2 * CELL_SIZE + MARGIN
                wx, wy = x + CELL_SIZE, y
                
            s = pygame.Surface((w_width, w_height), pygame.SRCALPHA)
            s.fill(color)
            self.screen.blit(s, (wx, wy))
            
    def draw_hud(self):
        # Text for info
        turn_text = f"Turn: {'RED' if self.game.turn == 0 else 'BLUE'}"
        p1_walls = self.game.players[0].walls_remaining
        p2_walls = self.game.players[1].walls_remaining
        
        txt_surf = self.font.render(turn_text, True, WHITE)
        self.screen.blit(txt_surf, (10, 10))
        
        info_txt = f"RED Walls: {p1_walls} | BLUE Walls: {p2_walls}"
        info_surf = self.font.render(info_txt, True, WHITE)
        self.screen.blit(info_surf, (10, 50))
        
        usage_txt = "Click: Move/Place | R: Rotate Wall | ESC: Menu"
        usage_surf = self.font.render(usage_txt, True, LIGHT_GRAY)
        self.screen.blit(usage_surf, (10, SCREEN_HEIGHT - 40))
        
        mode_txt = f"Mode: {self.selected_action}"
        mode_surf = self.font.render(mode_txt, True, GOLD)
        self.screen.blit(mode_surf, (SCREEN_WIDTH - 150, 10))

    def get_board_coords(self, mx, my):
        rx = mx - BOARD_OFFSET_X
        ry = my - BOARD_OFFSET_Y
        if rx < 0 or ry < 0: return -1, -1, False
        c = int(rx / (CELL_SIZE + MARGIN))
        r = int(ry / (CELL_SIZE + MARGIN))
        return r, c, True

    def is_mouse_on_board(self, mx, my):
        return (BOARD_OFFSET_X <= mx < BOARD_OFFSET_X + 9*(CELL_SIZE+MARGIN) and
                BOARD_OFFSET_Y <= my < BOARD_OFFSET_Y + 9*(CELL_SIZE+MARGIN))

    def handle_click(self, pos):
        r, c, _ = self.get_board_coords(*pos)
        
        # Decide action based on mode
        if self.selected_action == 'MOVE':
            if 0 <= r < 9 and 0 <= c < 9:
                if self.game.move_pawn(r, c):
                    self.check_win()
        elif self.selected_action == 'WALL':
             if 0 <= r < 8 and 0 <= c < 8:
                 if self.game.place_wall(r, c, self.wall_orientation):
                     pass
    
    def check_win(self):
        winner = None
        for i, p in enumerate(self.game.players):
            if p.has_won():
                winner = i
                break
        if winner is not None:
             print(f"Player {winner} WINS!")
             # Maybe go back to menu or show win screen?
             # For now, print and reset
             # self.game = QuoridorGame()
             
             # Let's verify win by resetting? Or just stop?
             # Back to menu is safer
             self.state = 'MENU'
             self.game = QuoridorGame()

    def handle_input(self, event):
        if self.state == 'MENU':
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_menu_click(event.pos)
            return
            
        # GAME Input
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left Click
                self.handle_click(event.pos)
            elif event.button == 3: # Right Click
                self.toggle_orientation()
                
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.toggle_orientation()
                
            elif event.key == pygame.K_m:
                 # Toggle mode? maybe not needed if we rely on click context? 
                 # But requested feature was "wall on space... copy insert".
                 # Let's keep 'M' to toggle between Move and Wall modes if user wants manual switch?
                 # Actually, let's make it automatic? 
                 # User said "Menu... save game...".
                 # Let's keep explicit mode toggle to be safe for now, as UI shows "Mode: WALL".
                 self.selected_action = 'WALL' if self.selected_action == 'MOVE' else 'MOVE'
                 
            elif event.key == pygame.K_ESCAPE:
                self.state = 'MENU'

            # WASD for P1?
            if self.game.turn == 0:
                 self.handle_wasd(event.key)

    def handle_wasd(self, key):
         # W=Up (-1, 0), S=Down (1, 0), A=Left (0, -1), D=Right (0, 1)
        dr, dc = 0, 0
        if key == pygame.K_w: dr = -1
        elif key == pygame.K_s: dr = 1
        elif key == pygame.K_a: dc = -1
        elif key == pygame.K_d: dc = 1
        
        if dr != 0 or dc != 0:
            curr = self.game.current_player()
            target_r, target_c = curr.r + dr, curr.c + dc
            
            # Simple move
            if (target_r, target_c) in self.game.get_valid_pawn_moves():
                self.game.move_pawn(target_r, target_c)
                self.check_win()
            else:
                # Try Jump
                jump_r, jump_c = curr.r + 2*dr, curr.c + 2*dc
                if (jump_r, jump_c) in self.game.get_valid_pawn_moves():
                    self.game.move_pawn(jump_r, jump_c)
                    self.check_win()

    def toggle_orientation(self):
        self.wall_orientation = 'V' if self.wall_orientation == 'H' else 'H'
