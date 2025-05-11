import tkinter as tk
import os
import subprocess
import sys
import threading
from PIL import Image, ImageTk
import pygame

class StageSelection(tk.Tk):
    def __init__(self):
        super().__init__()
        pygame.mixer.init()
        self.title("Starry Night - Stage Selection")
        self.geometry("1280x720")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.quit_game)
        self.sfx_path = "sfx/menu"
        self.sounds = self.load_sounds()
        self.bg_image = Image.open("bg.png")
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        self.canvas = tk.Canvas(self, width=1280, height=720)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
        self.init_ui()
        self.game_process = None
        pygame.mixer.music.load("sfx/menu/nier_rain.wav")
        pygame.mixer.music.play(-1)

    def load_sound(self, path):
        try:
            sound = pygame.mixer.Sound(path)
            print(f"Loaded sound: {path}")
            return sound
        except pygame.error as e:
            print(f"Error loading sound ({path}): {e}")
            return None

    def load_sounds(self):
        sounds = {}
        sound_files = {"click": "select.wav", "back": "back.wav"}
        for key, filename in sound_files.items():
            path = os.path.join(self.sfx_path, filename)
            if os.path.exists(path):
                sounds[key] = self.load_sound(path)
            else:
                print(f"Warning: Sound file not found at {path}")
        return sounds

    def play_sound(self, sound_key):
        sound = self.sounds.get(sound_key)
        if sound:
            sound.play()

    def init_ui(self):
        title_label = tk.Label(self, text="Starry Night", font=('Small Fonts', 58, "bold"), bg="#000000", fg="white")

        s1_button = tk.Button(self, text="Visor", font=('Small Fonts', 24), width=30,
                              command=lambda: [self.play_sound("click"), self.start_game(1)])
        s2_button = tk.Button(self, text="Dunky", font=('Small Fonts', 24), width=30,
                              command=lambda: [self.play_sound("click"), self.start_game(2)])
        stats_button = tk.Button(self, text="Statistic", font=('Small Fonts', 24), width=30, command=self.stats)
        quit_button = tk.Button(self, text="Back to Main Menu", font=('Small Fonts', 24), width=30,
                                command=lambda: [self.play_sound("click"), self.main_menu()])

        self.canvas.create_window(640, 120, window=title_label)
        self.canvas.create_window(640, 260, window=s1_button)
        self.canvas.create_window(640, 340, window=s2_button)
        self.canvas.create_window(640, 420, window=stats_button)
        self.canvas.create_window(640, 500, window=quit_button)

    def start_game(self, lvl):
        try:
            current_directory = os.path.dirname(os.path.realpath(__file__))
            game_script = os.path.join(current_directory, "combat_turn_based.py")

            if not os.path.exists(game_script):
                raise FileNotFoundError(f"Could not find {game_script}")

            def run_game():
                try:
                    pygame.mixer.music.stop()
                    self.withdraw()
                    self.game_process = subprocess.Popen([sys.executable, game_script, str(lvl)])
                    self.game_process.wait()
                    self.deiconify()
                    self.game_process = None
                except Exception as e:
                    print(f"Error running game: {e}")
                    self.deiconify()
                    self.game_process = None

            threading.Thread(target=run_game).start()

        except Exception as e:
            tk.messagebox.showerror("Error", f"Could not launch game: {e}")
            print(f"Error in start_game: {e}")

    def stats(self):
        try:
            current_directory = os.path.dirname(os.path.realpath(__file__))
            game_script = os.path.join(current_directory, "statistic.py")

            if not os.path.exists(game_script):
                raise FileNotFoundError(f"Could not find {game_script}")

            def run_game():
                try:
                    pygame.mixer.music.stop()
                    self.withdraw()
                    self.game_process = subprocess.Popen([sys.executable, game_script])
                    self.game_process.wait()
                    self.deiconify()
                    self.game_process = None
                except Exception as e:
                    print(f"Error running game: {e}")
                    self.deiconify()
                    self.game_process = None

            threading.Thread(target=run_game).start()

        except Exception as e:
            tk.messagebox.showerror("Error", f"Could not launch game: {e}")
            print(f"Error in start_game: {e}")

    def main_menu(self):
        pygame.mixer.music.stop()
        self.destroy()

    def quit_game(self):
        pygame.mixer.music.stop()
        if self.game_process:
            self.game_process.terminate()
            self.game_process.wait()
        self.destroy()


if __name__ == "__main__":
    app = StageSelection()
    app.mainloop()