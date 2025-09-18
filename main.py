import arcade
import random
import math

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Hey, That's My Fish!"

HEX_RADIUS = 30
HEX_SPACING_X = HEX_RADIUS * 1.5
HEX_SPACING_Y = HEX_RADIUS * 1.732 

BOARD_ROWS = 8
BOARD_COLS = 8

class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.BLACK)
        
        self.board = []
        self.selected_penguin = None
        self.current_player = 'human'
        
        self.setup_board()

    def setup_board(self):
        self.board = [[{} for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                fish_count = random.randint(1, 3)
                self.board[row][col]['fish'] = fish_count
                self.board[row][col]['penguin'] = None
                self.board[row][col]['is_hole'] = False
        
        # Initial Penguin Placement 
        self.board[2][2]['penguin'] = 'human'
        self.board[5][5]['penguin'] = 'ai'
        
    def on_draw(self):
        self.clear()
        self.draw_highlights()
        self.draw_hex_grid()

    def update(self, delta_time):
        """All the game logic goes here."""
        pass
    
    def on_mouse_press(self, x, y, button, modifiers):
        if self.current_player == 'human':
            if self.selected_penguin is not None:
                dest_row, dest_col = self.get_hex_from_mouse(x, y)
                
                valid_moves = self.get_valid_moves(self.selected_penguin[0], self.selected_penguin[1])
                if (dest_row, dest_col) in valid_moves:
                    start_row, start_col = self.selected_penguin
                    self.move_penguin(self.selected_penguin, (dest_row, dest_col))
                    self.selected_penguin = None
                    print(f"Moved penguin from ({start_row}, {start_col}) to ({dest_row}, {dest_col})")
                else:
                    self.selected_penguin = None
                    print("Invalid move or click, deselected penguin.")

            else:
                penguin_found, row, col = self.get_penguin_at_mouse(x, y)
                if penguin_found:
                    self.selected_penguin = (row, col)
                    print(f"Selected a human penguin at ({row}, {col})")
    
    def get_penguin_at_mouse(self, x, y):
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if self.board[row][col]['penguin'] == 'human':
                    hex_x, hex_y = self.get_hex_center(row, col)
                    if (x - hex_x)**2 + (y - hex_y)**2 < (HEX_RADIUS)**2:
                        return True, row, col
        return False, None, None

    def get_hex_from_mouse(self, x, y):
        x_adj = x - 50
        y_adj = y - 50

        row = round(y_adj / HEX_SPACING_Y)
        col = round(x_adj / HEX_SPACING_X)
        
        if row % 2 == 1:
            col = round((x_adj - HEX_SPACING_X / 2) / HEX_SPACING_X)
        
        if 0 <= row < BOARD_ROWS and 0 <= col < BOARD_COLS:
            return row, col
        else:
            return -1, -1

    def move_penguin(self, start_pos, end_pos):
        start_row, start_col = start_pos
        end_row, end_col = end_pos

        self.board[end_row][end_col]['penguin'] = self.board[start_row][start_col]['penguin']
        self.board[start_row][start_col]['penguin'] = None
        self.board[start_row][start_col]['is_hole'] = True

    def get_hex_center(self, row, col):
        x = col * HEX_SPACING_X
        y = row * HEX_SPACING_Y
        if row % 2 == 1:
            x += HEX_SPACING_X / 2
        
        center_x = x + 50
        center_y = y + 50
        return center_x, center_y

    def draw_highlights(self):
        if self.selected_penguin:
            sel_row, sel_col = self.selected_penguin
            
            x, y = self.get_hex_center(sel_row, sel_col)
            arcade.draw_circle_filled(x, y, HEX_RADIUS, arcade.color.YELLOW_ORANGE)

            valid_moves = self.get_valid_moves(sel_row, sel_col)
            for row, col in valid_moves:
                x, y = self.get_hex_center(row, col)
                arcade.draw_circle_filled(x, y, HEX_RADIUS, arcade.color.LIME_GREEN)

    def get_valid_moves(self, row, col):
        valid_moves = []
        directions = [
            (0, 1),    # Right
            (0, -1),   # Left
            (-1, 0),   # Up-Right (for even rows) / Up-Left (for odd rows)
            (-1, 1),   # Up-Left (for even rows) / Up-Right (for odd rows)
            (1, 0),    # Down-Left (for even rows) / Down-Right (for odd rows)
            (1, 1)     # Down-Right (for even rows) / Down-Left (for odd rows)
        ]

        for dr, dc in directions:
            current_row, current_col = row, col
            while True:
                # This is a key step to correctly handle staggered hex movement
                is_even_row = (current_row % 2 == 0)
                
                next_row = current_row + dr
                next_col = current_col + dc
                
                if dr != 0:
                    if is_even_row:
                        next_col = current_col + dc
                    else:
                        next_col = current_col + dc + 1
                
                current_row, current_col = next_row, next_col
                
                if not (0 <= current_row < BOARD_ROWS and 0 <= current_col < BOARD_COLS):
                    break

                if self.board[current_row][current_col]['is_hole'] or self.board[current_row][current_col]['penguin']:
                    break
            
                valid_moves.append((current_row, current_col))

        return valid_moves

    def draw_hex_grid(self):
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                x, y = self.get_hex_center(row, col)

                if self.board[row][col]['is_hole']:
                    continue
                
                points = []
                for i in range(6):
                    angle_deg = 60 * i
                    angle_rad = math.radians(angle_deg)
                    point_x = x + HEX_RADIUS * math.cos(angle_rad)
                    point_y = y + HEX_RADIUS * math.sin(angle_rad)
                    points.append((point_x, point_y))

                arcade.draw_polygon_filled(points, arcade.color.LIGHT_BLUE)
                
                inner_points = []
                inner_radius = HEX_RADIUS - 5
                for i in range(6):
                    angle_deg = 60 * i
                    angle_rad = math.radians(angle_deg)
                    point_x = x + inner_radius * math.cos(angle_rad)
                    point_y = y + inner_radius * math.sin(angle_rad)
                    inner_points.append((point_x, point_y))
                arcade.draw_polygon_filled(inner_points, arcade.color.WHITE)

                # Draw the fish
                if self.board[row][col]['fish']:
                    fish_color = arcade.color.YELLOW if self.board[row][col]['fish'] == 1 else arcade.color.ORANGE
                    arcade.draw_circle_filled(x, y, 5, fish_color)

                # Draw the penguin if one exists
                if self.board[row][col]['penguin'] == 'human':
                    arcade.draw_circle_filled(x, y, 10, arcade.color.DARK_BLUE)
                elif self.board[row][col]['penguin'] == 'ai':
                    arcade.draw_circle_filled(x, y, 10, arcade.color.GREEN)


def main():
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()

if __name__ == "__main__":
    main()