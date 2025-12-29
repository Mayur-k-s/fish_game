import arcade
import random
import math

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Hey, That's My Fish!"
#tile size
HEX_RADIUS = 30
HEX_SPACING_X = HEX_RADIUS * 1.5
HEX_SPACING_Y = HEX_RADIUS * 1.732

BOARD_ROWS = 8
BOARD_COLS = 8

TURN_TIME_LIMIT = 10.0

class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.BLACK)

        self.board = []
        self.selected_penguin = None
        self.current_player = 'human'
        
        self.human_score = 0
        self.ai_score = 0
        self.turn_timer = TURN_TIME_LIMIT

        self.setup_board()
        
        # New, more reliable way to call the game logic loop
        arcade.schedule(self.on_update, 1/60)

    def setup_board(self):
        self.board = [[{} for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                fish_count = random.randint(1, 3)
                self.board[row][col]['fish'] = fish_count
                self.board[row][col]['penguin'] = None
                self.board[row][col]['is_hole'] = False

        self.board[2][2]['penguin'] = 'human'
        self.board[5][5]['penguin'] = 'ai'

    def on_draw(self):
        self.clear()
        self.draw_highlights()
        self.draw_hex_grid()
        self.draw_ui()

    def on_update(self, delta_time):
        # This function is now scheduled to run 60 times per second
        self.turn_timer -= delta_time
        if self.turn_timer <= 0:
            self.switch_turn()

        if self.current_player == 'ai':
            # AI will make a move after a short delay
            if self.turn_timer < 9.0:
                self.execute_ai_turn()

    def draw_ui(self):
        arcade.draw_text(f"Your Score: {self.human_score}",
                         10, SCREEN_HEIGHT - 30, arcade.color.WHITE, 16)
        arcade.draw_text(f"AI Score: {self.ai_score}",
                         SCREEN_WIDTH - 140, SCREEN_HEIGHT - 30, arcade.color.WHITE, 16)
        
        turn_text = "Your Turn" if self.current_player == 'human' else "AI's Turn"
        arcade.draw_text(turn_text, SCREEN_WIDTH / 2, SCREEN_HEIGHT - 30, arcade.color.WHITE, 18, anchor_x="center")

        timer_color = arcade.color.WHITE
        if self.turn_timer < 5:
            timer_color = arcade.color.RED_ORANGE
        # Display the timer, ensuring it doesn't go below 0
        display_time = max(0, int(self.turn_timer))
        arcade.draw_text(f"Time: {display_time}",
                         SCREEN_WIDTH / 2, SCREEN_HEIGHT - 60, timer_color, 14, anchor_x="center")

    def on_mouse_press(self, x, y, button, modifiers):
        if self.current_player == 'human':
            if self.selected_penguin is not None:
                dest_row, dest_col = self.get_hex_from_mouse(x, y)
                valid_moves = self.get_valid_moves(self.selected_penguin[0], self.selected_penguin[1])
                if (dest_row, dest_col) in valid_moves:
                    self.move_penguin(self.selected_penguin, (dest_row, dest_col))
                else:
                    self.selected_penguin = None
            else:
                penguin_found, row, col = self.get_penguin_at_mouse(x, y)
                if penguin_found:
                    self.selected_penguin = (row, col)

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
        row = round(y_adj / (HEX_SPACING_Y * 0.75))
        if row % 2 == 1:
            col = round((x_adj - HEX_SPACING_X / 2) / HEX_SPACING_X)
        else:
            col = round(x_adj / HEX_SPACING_X)
        if 0 <= row < BOARD_ROWS and 0 <= col < BOARD_COLS:
            return row, col
        else:
            return -1, -1

    def move_penguin(self, start_pos, end_pos):
        start_row, start_col = start_pos
        end_row, end_col = end_pos
        player_type = self.board[start_row][start_col]['penguin']
        fish_collected = self.board[start_row][start_col]['fish']
        if player_type == 'human':
            self.human_score += fish_collected
        else:
            self.ai_score += fish_collected
        self.board[end_row][end_col]['penguin'] = player_type
        self.board[start_row][start_col]['penguin'] = None
        self.board[start_row][start_col]['is_hole'] = True
        self.switch_turn()

    def switch_turn(self):
        self.current_player = 'ai' if self.current_player == 'human' else 'human'
        self.turn_timer = TURN_TIME_LIMIT
        self.selected_penguin = None

    def get_hex_center(self, row, col):
        x = col * HEX_SPACING_X
        y = row * HEX_SPACING_Y * 0.75
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

    def offset_to_cube(self, row, col):
        x = col - (row - (row & 1)) / 2
        z = row
        y = -x - z
        return x, y, z

    def cube_to_offset(self, x, y, z):
        col = int(x + (z - (z & 1)) / 2)
        row = int(z)
        return row, col

    def get_valid_moves(self, row, col):
        valid_moves = []
        start_cube = self.offset_to_cube(row, col)
        cube_directions = [(1, -1, 0), (-1, 1, 0), (1, 0, -1), (-1, 0, 1), (0, 1, -1), (0, -1, 1)]
        for dx, dy, dz in cube_directions:
            current_cube = list(start_cube)
            while True:
                current_cube[0] += dx
                current_cube[1] += dy
                current_cube[2] += dz
                next_row, next_col = self.cube_to_offset(*current_cube)
                if not (0 <= next_row < BOARD_ROWS and 0 <= next_col < BOARD_COLS):
                    break
                if self.board[next_row][next_col]['is_hole'] or self.board[next_row][next_col]['penguin']:
                    break
                valid_moves.append((next_row, next_col))
        return valid_moves

    def execute_ai_turn(self):
        all_possible_moves = []
        ai_penguins = []
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                if self.board[r][c]['penguin'] == 'ai':
                    ai_penguins.append((r, c))
        for r_start, c_start in ai_penguins:
            valid_moves = self.get_valid_moves(r_start, c_start)
            for r_end, c_end in valid_moves:
                score = self.board[r_end][c_end]['fish']
                all_possible_moves.append({'start': (r_start, c_start), 'end': (r_end, c_end), 'score': score})
        if not all_possible_moves:
            self.switch_turn()
            return
        best_move = max(all_possible_moves, key=lambda move: move['score'])
        self.move_penguin(best_move['start'], best_move['end'])

    def draw_hex_grid(self):
        # The size of the gap between hexes
        gap = 2
        draw_radius = HEX_RADIUS - gap

        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if self.board[row][col]['is_hole']:
                    continue
                x, y = self.get_hex_center(row, col)
                points = []
                for i in range(6):
                    angle_deg = 60 * i
                    angle_rad = math.radians(angle_deg)
                    # Use the smaller draw_radius to create the gap
                    point_x = x + draw_radius * math.cos(angle_rad)
                    point_y = y + draw_radius * math.sin(angle_rad)
                    points.append((point_x, point_y))
                arcade.draw_polygon_filled(points, arcade.color.LIGHT_BLUE)
                
                inner_points = []
                inner_radius = draw_radius - 5
                for i in range(6):
                    angle_deg = 60 * i
                    angle_rad = math.radians(angle_deg)
                    point_x = x + inner_radius * math.cos(angle_rad)
                    point_y = y + inner_radius * math.sin(angle_rad)
                    inner_points.append((point_x, point_y))
                arcade.draw_polygon_filled(inner_points, arcade.color.WHITE)

                if self.board[row][col]['fish']:
                    fish_color = arcade.color.YELLOW if self.board[row][col]['fish'] == 1 else arcade.color.ORANGE
                    arcade.draw_circle_filled(x, y, 5, fish_color)
                if self.board[row][col]['penguin'] == 'human':
                    arcade.draw_circle_filled(x, y, 10, arcade.color.DARK_BLUE)
                elif self.board[row][col]['penguin'] == 'ai':
                    arcade.draw_circle_filled(x, y, 10, arcade.color.GREEN)

def main():
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()

if __name__ == "__main__":
    main()
