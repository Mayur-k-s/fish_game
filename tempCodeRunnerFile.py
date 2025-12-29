    if self.background_music:
        try:
            self.current_music_player = arcade.play_sound(self.background_music, volume=0.4)
        except Exception as e:
            print(f"Error starting music: {e}")
            self.current_music_player = None