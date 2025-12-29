import arcade
import random
import math
from arcade.gui import UIManager, UIFlatButton, UIBoxLayout


SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 675
SCREEN_TITLE = "Hey, That's My Fish!"

HEX_RADIUS = 44
HEX_SPACING_X = HEX_RADIUS * 1.7
HEX_SPACING_Y = HEX_RADIUS * 1.932

BOARD_ROWS = 8
BOARD_COLS = 8
TURN_TIME_LIMIT = 30.0
BLINK_TIME = 0.4  


TOP_BAR_HEIGHT = 80
BOTTOM_BAR_HEIGHT = 60 

class MyGame(arcade.View):
    def __init__(self): 
        super().__init__()
        arcade.set_background_color(arcade.color.BLACK)

        # Game state variables
        self.board = []
        self.selected_penguin = None
        self.current_player = 'human'
        self.placement_selected = False
        self.human_score = 0
        self.ai_score = 0
        self.turn_timer = TURN_TIME_LIMIT
        self.game_phase = 'placement'
        self.unplaced_human_penguins = 3
        self.unplaced_ai_penguins = 3
        self.offset_x, self.offset_y = self.calculate_board_offset()

        # blinking time
        self.highlight_blink_timer = 0.0
        self.show_highlight = True

        # Fish sprites list
        self.fish_sprite_list = arcade.SpriteList()

        #Loading Sound Effects
        try:
            self.move_sound = arcade.load_sound(":resources:sounds/jump1.wav")
            self.score_sound = arcade.load_sound(":resources:sounds/coin1.wav")
            self.invalid_sound = arcade.load_sound(":resources:sounds/error1.wav")
            self.win_sound = arcade.load_sound(":resources:sounds/upgrade1.wav")
            self.lose_sound = arcade.load_sound(":resources:sounds/laser1.wav")
            self.button_click_sound = arcade.load_sound(":resources:sounds/hit1.wav")
            self.isolated_sound = arcade.load_sound(":resources:sounds/error2.wav")
            self.background_music = arcade.load_sound(":resources:music/funkyrobot.mp3")
            self.current_music_player = None

            #Loading clicking_coin.wav
            try:
                self.select_sound = arcade.load_sound("sound.wav")
                print("Loaded custom 'clicking_coin.wav' successfully")
            except Exception as select_e:
                print(f"!!! WARNING: Could not load clicking_coin.wav ({select_e}). Using default coin sound. !!!")
                self.select_sound = arcade.load_sound(":resources:sounds/coin2.wav") 
            print("Sounds and Music loaded successfully")
            
        except Exception as e:
            print(f"WARNING: Could not load some sounds/music: {e}")
            self.move_sound = None
            self.score_sound = None
            self.invalid_sound = None
            self.win_sound = None
            self.select_sound = None
            self.lose_sound = None
            self.button_click_sound = None
            self.isolated_sound = None
            self.background_music = None
            self.current_music_player = None

        if self.background_music:
            try:
                 self.current_music_player = arcade.play_sound(self.background_music, volume=0.4) # Plays once
                 print("Background music started (will play once)")
            except Exception as e:
                 print(f"ERROR starting background music: {e}")
                 self.current_music_player = None

        self.ui_manager = UIManager()
        self.ui_manager.enable()
        self.exit_button = UIFlatButton( text="Exit", width=80, height=30 )
        button_margin = 15
        self.exit_button.center_x = (self.exit_button.width / 2) + button_margin
        self.exit_button.center_y = (self.exit_button.height / 2) + button_margin
        self.exit_button.on_click = self.exit_game
        self.ui_manager.add(self.exit_button)

        self.setup_board()
        arcade.schedule(self.on_update, 1 / 60)

    def on_show_view(self):
        self.ui_manager.enable()
        if self.background_music and not self.current_music_player:
             try:
                 self.current_music_player = arcade.play_sound(self.background_music, volume=0.4)
             except Exception as e:
                 print(f"ERROR restarting background music: {e}")
                 self.current_music_player = None

    def on_hide_view(self):
        if hasattr(self, 'current_music_player') and self.current_music_player:
            arcade.stop_sound(self.current_music_player)
            self.current_music_player = None

    def calculate_board_offset(self):
        board_width = BOARD_COLS * HEX_SPACING_X + HEX_RADIUS
        board_height = (BOARD_ROWS - 1) * HEX_SPACING_Y * 0.75 + (2 * HEX_RADIUS)
        offset_x = (SCREEN_WIDTH - board_width) / 2
        playable_area_height = SCREEN_HEIGHT - TOP_BAR_HEIGHT - BOTTOM_BAR_HEIGHT
        vertical_padding = (playable_area_height - board_height) / 2
        offset_y = BOTTOM_BAR_HEIGHT + vertical_padding + HEX_RADIUS
        return offset_x, offset_y

    def setup_board(self):
        self.board = [[{} for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
        self.fish_sprite_list = arcade.SpriteList()

        base_path = "/Users/mayur/Desktop/fish_game/"
        fish_image_paths = {
            1: base_path + "fish1.png",
            2: base_path + "fish2.png",
            3: base_path + "fish3.png",
        }

        one_fish_count = int((BOARD_ROWS * BOARD_COLS) * 0.6)
        two_fish_count = int((BOARD_ROWS * BOARD_COLS) * 0.3)
        three_fish_count = (BOARD_ROWS * BOARD_COLS) - one_fish_count - two_fish_count
        fish_counts = ([1] * one_fish_count +
                       [2] * two_fish_count +
                       [3] * three_fish_count)
        random.shuffle(fish_counts)

        target_sprite_size = HEX_RADIUS * 1.5

        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if not fish_counts: fish_count = 1
                else: fish_count = fish_counts.pop()

                self.board[row][col]['fish'] = fish_count
                self.board[row][col]['penguin'] = None
                self.board[row][col]['is_hole'] = False

                if fish_count in fish_image_paths:
                    image_path = fish_image_paths[fish_count]
                    try:
                        fish_sprite = arcade.Sprite(image_path)
                        aspect_ratio = fish_sprite.texture.width / fish_sprite.texture.height
                        if aspect_ratio > 1:
                            fish_sprite.width = target_sprite_size
                            fish_sprite.height = target_sprite_size / aspect_ratio
                        else:
                            fish_sprite.height = target_sprite_size
                            fish_sprite.width = target_sprite_size * aspect_ratio
                        fish_sprite.center_x, fish_sprite.center_y = self.get_hex_center(row, col)
                        fish_sprite.properties['grid_row'] = row
                        fish_sprite.properties['grid_col'] = col
                        self.fish_sprite_list.append(fish_sprite)
                    except FileNotFoundError:
                        print(f"!!! CRITICAL ERROR: Fish image not found for count {fish_count}. Check path: '{image_path}'. !!!")
                    except Exception as e:
                         print(f"!!! WARNING: Error creating fish sprite for count {fish_count}: {e} !!!")

    def on_draw(self):
        self.clear()
        self.draw_hex_grid()
        self.fish_sprite_list.draw()
        self.draw_highlights()
        self.draw_penguins()
        self.draw_ui()
        self.draw_unplaced_penguins()
        self.ui_manager.draw()

    def draw_unplaced_penguins(self):
        start_x = 50
        start_y = 100
        for i in range(self.unplaced_human_penguins):
            color = arcade.color.YELLOW_ORANGE if self.placement_selected and i == self.unplaced_human_penguins - 1 else arcade.color.DARK_BLUE
            arcade.draw_circle_filled(start_x, start_y + i * 30, 10, color)
        for i in range(self.unplaced_ai_penguins):
            arcade.draw_circle_filled(SCREEN_WIDTH - start_x, start_y + i * 30, 10, arcade.color.GREEN)

    def on_update(self, delta_time):
        self.highlight_blink_timer += delta_time
        if self.highlight_blink_timer > BLINK_TIME:
            self.show_highlight = not self.show_highlight
            self.highlight_blink_timer = 0.0

        self.turn_timer -= delta_time
        if self.turn_timer <= 0: self.switch_turn()

        if self.current_player == 'ai' and self.game_phase in ['placement', 'game_in_progress']:
            if self.turn_timer < (TURN_TIME_LIMIT - 0.5): self.execute_ai_turn()

        if self.game_phase == 'placement' and self.unplaced_human_penguins == 0 and self.unplaced_ai_penguins == 0:
            self.game_phase = 'game_in_progress'
            self.current_player = 'human'
            self.turn_timer = TURN_TIME_LIMIT

    def on_mouse_press(self, x, y, button, modifiers):
        if self.ui_manager.on_mouse_press(x, y, button, modifiers): return
        if self.current_player != 'human': return

        dest_row, dest_col = self.get_hex_from_mouse(x, y)
        is_on_board = (dest_row != -1)

        if self.game_phase == 'placement':
            if not is_on_board:
                if self.get_unplaced_penguin_at_mouse(x, y): self.placement_selected = True
                return

            if is_on_board and self.placement_selected:
                if self.board[dest_row][dest_col]['penguin'] is None and self.board[dest_row][dest_col]['fish'] == 1:
                    self.board[dest_row][dest_col]['penguin'] = 'human'
                    self.unplaced_human_penguins -= 1
                    self.placement_selected = False
                    self.switch_turn()
                else:
                    self.placement_selected = False
                    if self.invalid_sound: arcade.play_sound(self.invalid_sound, volume=1.0)
                return

        if self.game_phase == 'game_in_progress' and is_on_board:
            if self.selected_penguin:
                 valid_moves = self.get_valid_moves(*self.selected_penguin)
                 if (dest_row, dest_col) in valid_moves:
                     self.move_penguin(self.selected_penguin, (dest_row, dest_col))
                 elif self.board[dest_row][dest_col]['penguin'] == 'human':
                     if not self.get_valid_moves(dest_row, dest_col):
                         if self.isolated_sound: arcade.play_sound(self.isolated_sound, volume=1.0)
                     else:
                         self.selected_penguin = (dest_row, dest_col)
                         if self.select_sound: arcade.play_sound(self.select_sound, volume=1.0)
                 else:
                     if self.invalid_sound: arcade.play_sound(self.invalid_sound, volume=1.0)
                     self.selected_penguin = None
            else:
                if self.board[dest_row][dest_col]['penguin'] == 'human':
                    if not self.get_valid_moves(dest_row, dest_col):
                        if self.isolated_sound: arcade.play_sound(self.isolated_sound, volume=1.0)
                    else:
                        self.selected_penguin = (dest_row, dest_col)
                        if self.select_sound: arcade.play_sound(self.select_sound, volume=1.0)
                else:
                    if self.invalid_sound: arcade.play_sound(self.invalid_sound, volume=1.0)

    def execute_ai_turn(self):
        if self.game_phase == 'placement' and self.unplaced_ai_penguins > 0:
            valid = [(r, c) for r in range(BOARD_ROWS) for c in range(BOARD_COLS)
                     if self.board[r][c]['penguin'] is None and self.board[r][c]['fish'] == 1]
            if valid:
                r, c = random.choice(valid)
                self.board[r][c]['penguin'] = 'ai'
                self.unplaced_ai_penguins -= 1
                self.switch_turn()
            else: self.switch_turn()
            return

        if self.game_phase == 'game_in_progress' and self.current_player == 'ai':
            all_moves = []
            ai_penguins = [(r, c) for r in range(BOARD_ROWS) for c in range(BOARD_COLS)
                           if self.board[r][c]['penguin'] == 'ai']
            for r, c in ai_penguins:
                for move in self.get_valid_moves(r, c):
                    er, ec = move
                    score = self.board[er][ec]['fish']
                    all_moves.append({'start': (r, c), 'end': move, 'score': score})
            if all_moves:
                best = max(all_moves, key=lambda m: m['score'])
                self.move_penguin(best['start'], best['end'])
            else: self.switch_turn()

    def get_unplaced_penguin_at_mouse(self, x, y):
        start_x, start_y = 50, 100
        for i in range(self.unplaced_human_penguins):
            if (x - start_x) ** 2 + (y - (start_y + i * 30)) ** 2 < 10 ** 2: return True
        return False

    def get_hex_from_mouse(self, x, y):
        x_adj, y_adj = x - self.offset_x, y - self.offset_y
        row = round(y_adj / (HEX_SPACING_Y * 0.75))
        col = round((x_adj - (HEX_SPACING_X / 2 if row % 2 else 0)) / HEX_SPACING_X)
        if 0 <= row < BOARD_ROWS and 0 <= col < BOARD_COLS:
            hex_x, hex_y = self.get_hex_center(row, col)
            if (x - hex_x)**2 + (y - hex_y)**2 < HEX_RADIUS**2: return row, col
        return -1, -1

    def move_penguin(self, start, end):
        sr, sc = start
        er, ec = end
        player = self.board[sr][sc]['penguin']
        fish = self.board[sr][sc]['fish']
        if player == 'human': self.human_score += fish
        else: self.ai_score += fish

        if self.move_sound: arcade.play_sound(self.move_sound, volume=1.0)
        if self.score_sound and fish > 1: arcade.play_sound(self.score_sound, volume=1.0)

        self.board[er][ec]['penguin'] = player
        self.board[sr][sc]['penguin'] = None
        self.board[sr][sc]['is_hole'] = True

        for fish_sprite in self.fish_sprite_list:
            sprite_row = fish_sprite.properties.get('grid_row')
            sprite_col = fish_sprite.properties.get('grid_col')
            if sprite_row == sr and sprite_col == sc:
                fish_sprite.remove_from_sprite_lists()
                break
        self.switch_turn()
        if self.check_game_over(): self.end_game()

    def switch_turn(self):
        self.current_player = 'ai' if self.current_player == 'human' else 'human'
        self.turn_timer = TURN_TIME_LIMIT
        self.selected_penguin = None
        if self.game_phase == 'game_in_progress':
            if not self.player_has_moves(self.current_player):
                other_player = 'ai' if self.current_player == 'human' else 'human'
                if not self.player_has_moves(other_player): self.end_game()
                else: self.switch_turn()

    def get_hex_center(self, row, col):
        x = col * HEX_SPACING_X
        y = row * HEX_SPACING_Y * 0.75
        if row % 2 == 1: x += HEX_SPACING_X / 2
        return x + self.offset_x, y + self.offset_y

    def get_hex_points(self, center_x, center_y, radius=HEX_RADIUS):
        points = []
        for i in range(6):
            angle_rad = math.radians(60 * i)
            x = center_x + radius * math.cos(angle_rad)
            y = center_y + radius * math.sin(angle_rad)
            points.append((x, y))
        return points

    def draw_highlights(self):
        if self.selected_penguin and self.show_highlight:
            sr, sc = self.selected_penguin
            x, y = self.get_hex_center(sr, sc)
            arcade.draw_polygon_filled(self.get_hex_points(x, y, HEX_RADIUS - 2), arcade.color.YELLOW_ORANGE)
            valid_moves = self.get_valid_moves(sr, sc)
            for (r, c) in valid_moves:
                x, y = self.get_hex_center(r, c)
                points = self.get_hex_points(x, y, HEX_RADIUS - 4)
                color = arcade.color.LIME_GREEN
                arcade.draw_polygon_filled(points, color)

    def offset_to_cube(self, row, col):
        x = col - (row - (row & 1)) / 2; z = row; y = -x - z
        return x, y, z

    def cube_to_offset(self, x, y, z):
        col = int(x + (z - (z & 1)) / 2); row = int(z)
        return row, col

    def get_valid_moves(self, row, col):
        moves = []
        start_cube = self.offset_to_cube(row, col)
        directions = [(1, -1, 0), (-1, 1, 0), (1, 0, -1), (-1, 0, 1), (0, 1, -1), (0, -1, 1)]
        for dx, dy, dz in directions:
            cur = list(start_cube)
            while True:
                cur[0] += dx; cur[1] += dy; cur[2] += dz
                r, c = self.cube_to_offset(*cur)
                if not (0 <= r < BOARD_ROWS and 0 <= c < BOARD_COLS): break
                if self.board[r][c]['is_hole'] or self.board[r][c]['penguin']: break
                moves.append((r, c))
        return moves

    def player_has_moves(self, player):
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                if self.board[r][c]['penguin'] == player:
                    if self.get_valid_moves(r, c): return True
        return False

    def check_game_over(self):
        if not self.player_has_moves('human') and not self.player_has_moves('ai'): return True
        return False

    def draw_hex_grid(self):
        gap = 2
        draw_radius = HEX_RADIUS - gap
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                if self.board[r][c]['is_hole']: continue
                x, y = self.get_hex_center(r, c)
                points = self.get_hex_points(x, y, draw_radius)
                arcade.draw_polygon_filled(points, arcade.color.POWDER_BLUE)

    def draw_penguins(self):
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                x, y = self.get_hex_center(r, c)
                if self.board[r][c]['penguin'] == 'human':
                    arcade.draw_circle_filled(x, y, 12, arcade.color.DARK_BLUE)
                    arcade.draw_circle_outline(x, y, 12, arcade.color.BLACK, 2)
                elif self.board[r][c]['penguin'] == 'ai':
                    arcade.draw_circle_filled(x, y, 12, arcade.color.GREEN)
                    arcade.draw_circle_outline(x, y, 12, arcade.color.BLACK, 2)

    def draw_ui(self):
        top_bar_points = [(0, SCREEN_HEIGHT - TOP_BAR_HEIGHT),(SCREEN_WIDTH, SCREEN_HEIGHT - TOP_BAR_HEIGHT),(SCREEN_WIDTH, SCREEN_HEIGHT),(0, SCREEN_HEIGHT)]
        arcade.draw_polygon_filled(top_bar_points, arcade.color.BLACK)
        bottom_bar_points = [(0, 0),(SCREEN_WIDTH, 0),(SCREEN_WIDTH, BOTTOM_BAR_HEIGHT),(0, BOTTOM_BAR_HEIGHT)]
        arcade.draw_polygon_filled(bottom_bar_points, arcade.color.BLACK)
        arcade.draw_text(f"Your Score: {self.human_score}", 100, SCREEN_HEIGHT - 30, arcade.color.WHITE, 16, anchor_x="center")
        arcade.draw_text(f"AI Score: {self.ai_score}", SCREEN_WIDTH - 100, SCREEN_HEIGHT - 30, arcade.color.WHITE, 16, anchor_x="center")
        turn_text = "Your Turn!" if self.current_player == 'human' else "AI's Turn!"
        if self.game_phase == 'placement': turn_text = f"Placement: {turn_text}"
        arcade.draw_text(turn_text, SCREEN_WIDTH / 2, SCREEN_HEIGHT - 30, arcade.color.WHITE, 18, anchor_x="center")
        timer_color = arcade.color.RED_ORANGE if self.turn_timer < 5 else arcade.color.WHITE
        arcade.draw_text(f"Time: {int(max(0, self.turn_timer))}", SCREEN_WIDTH / 2, SCREEN_HEIGHT - 60, timer_color, 14, anchor_x="center")

    def end_game(self):
        if self.human_score > self.ai_score:
            if self.win_sound:
                arcade.play_sound(self.win_sound, volume=1.0)
        elif self.ai_score > self.human_score:
            if self.lose_sound:
                arcade.play_sound(self.lose_sound, volume=1.0)
        self.ui_manager.disable()
        game_over_view = GameOverView(self.human_score, self.ai_score, self)
        self.window.show_view(game_over_view)

    def exit_game(self, event):
        if self.button_click_sound:
            arcade.play_sound(self.button_click_sound, volume=1.0)
        self.ui_manager.disable()
        confirmation_view = ExitConfirmationView(self)
        self.window.show_view(confirmation_view)

class GameOverView(arcade.View):
    def __init__(self, human_score, ai_score, game_view):
        super().__init__()
        self.game_view = game_view
        self.human_score = human_score
        self.ai_score = ai_score
        if human_score > ai_score:
            self.winner = "As I said!\n You are better than AI!"
            self.color = arcade.color.LIGHT_GREEN
        elif ai_score > human_score:
            self.winner = "OOPS!\n Come on, \n You can beat AI!"
            self.color = arcade.color.RED_ORANGE
        else:
            self.winner = "Relax! \n It's a Tie!"
            self.color = arcade.color.YELLOW

    def on_show_view(self): arcade.set_background_color(arcade.color.BLACK)
    def on_draw(self):
        self.clear()
        arcade.draw_text("Game Over!", SCREEN_WIDTH / 2, SCREEN_HEIGHT - 120, arcade.color.WHITE, 48, anchor_x="center")
        arcade.draw_text(f"Your Score: {self.human_score}", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 40, arcade.color.WHITE, 24, anchor_x="center")
        arcade.draw_text(f"AI Score: {self.ai_score}", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, arcade.color.WHITE, 24, anchor_x="center")
        arcade.draw_text(self.winner, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 70, self.color, 30, anchor_x="center", multiline=True, width=SCREEN_WIDTH*0.8,align="center")
        arcade.draw_text("Click to Restart", SCREEN_WIDTH / 2, 100, arcade.color.GRAY, 18, anchor_x="center")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        if self.game_view and hasattr(self.game_view, 'button_click_sound') and self.game_view.button_click_sound:
            arcade.play_sound(self.game_view.button_click_sound, volume=1.0)
        new_game_view = MyGame()
        self.window.show_view(new_game_view)

class ExitConfirmationView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view
        self.ui_manager = UIManager()
        self.ui_manager.enable()
        button_width = 100; button_height = 40; button_spacing = 20
        yes_button = UIFlatButton(text="Yes", width=button_width, height=button_height)
        yes_button.center_x = SCREEN_WIDTH / 2; yes_button.center_y = SCREEN_HEIGHT / 2 - button_spacing
        yes_button.on_click = self.on_yes_click
        self.ui_manager.add(yes_button)
        no_button = UIFlatButton(text="No", width=button_width, height=button_height)
        no_button.center_x = SCREEN_WIDTH / 2; no_button.center_y = SCREEN_HEIGHT / 2 - button_height - (button_spacing * 2)
        no_button.on_click = self.on_no_click
        self.ui_manager.add(no_button)

    def on_show_view(self): arcade.set_background_color(arcade.color.DARK_BLUE_GRAY); self.ui_manager.enable()
    def on_hide_view(self): self.ui_manager.disable()
    def on_draw(self):
        self.clear()
        arcade.draw_text("Are you sure you want to exit?", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100, arcade.color.WHITE_SMOKE, font_size=24, anchor_x="center")
        self.ui_manager.draw()

    def on_yes_click(self, event):
        if self.game_view and hasattr(self.game_view, 'button_click_sound') and self.game_view.button_click_sound:
            arcade.play_sound(self.game_view.button_click_sound, volume=1.0)
        game_over_view = GameOverView(self.game_view.human_score, self.game_view.ai_score, self.game_view)
        self.window.show_view(game_over_view)

    def on_no_click(self, event):
        if self.game_view and hasattr(self.game_view, 'button_click_sound') and self.game_view.button_click_sound:
            arcade.play_sound(self.game_view.button_click_sound, volume=1.0)
        self.window.show_view(self.game_view)
        if hasattr(self.game_view, 'ui_manager'): self.game_view.ui_manager.enable()

def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=False)
    game_view = MyGame()
    window.show_view(game_view)
    arcade.run()

if __name__ == "__main__":
    main()