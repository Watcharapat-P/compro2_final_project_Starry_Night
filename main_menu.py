import tkinter as tk
import os
import subprocess
import sys
import threading
import pygame
from PIL import Image, ImageTk

class BaseMenu(tk.Tk):
    def __init__(self, title):
        super().__init__()
        pygame.mixer.init()
        self.title(title)
        self.geometry("1280x720")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.quit_game)
        self.game_process = None
        self.sfx_path = "sfx/menu"
        self.sounds = self.load_sounds()
        try:
            self.bg_image = Image.open("bg.png")
            self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        except FileNotFoundError:
            self.bg_photo = None
            print("Warning: bg.png not found.")
        self.canvas = tk.Canvas(self, width=1280, height=720)
        self.canvas.pack(fill="both", expand=True)
        if self.bg_photo:
            self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
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

    def run_script(self, script_name, *args):
        try:
            current_directory = os.path.dirname(os.path.realpath(__file__))
            script_path = os.path.join(current_directory, script_name)

            if not os.path.exists(script_path):
                raise FileNotFoundError(f"Could not find {script_path}")

            def run_process():
                try:
                    pygame.mixer.music.stop()
                    self.withdraw()
                    command = [sys.executable, script_path] + [str(arg) for arg in args]
                    self.game_process = subprocess.Popen(command)
                    self.game_process.wait()
                    self.deiconify()
                    self.game_process = None
                except Exception as e:
                    print(f"Error running {script_name}: {e}")
                    self.deiconify()
                    self.game_process = None

            threading.Thread(target=run_process).start()

        except Exception as e:
            tk.messagebox.showerror("Error", f"Could not launch {script_name}: {e}")
            print(f"Error in run_script for {script_name}: {e}")

    def quit_game(self):
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        if self.game_process:
            self.game_process.terminate()
            self.game_process.wait()
        self.destroy()

class StarryNightMainMenu(BaseMenu):
    def __init__(self):
        super().__init__("Starry Night - Main Menu")
        self.init_ui()

    def init_ui(self):
        title_label = tk.Label(self, text="Starry Night", font=('Small Fonts', 58, "bold"), bg="#000000", fg="white")
        start_button = tk.Button(self, text="Start", font=('Small Fonts', 32), width=30,
                                 command=lambda: [self.play_sound("click"), self.open_stage_selection()])
        stats_button = tk.Button(self, text="Statistic", font=('Small Fonts', 32), width=30,
                                 command=lambda: [self.play_sound("click"), self.run_script("statistic.py")])
        quit_button = tk.Button(self, text="Quit", font=('Small Fonts', 32), width=30,
                                command=lambda: [self.play_sound("back"), self.quit_game()])

        self.canvas.create_window(640, 120, window=title_label)
        self.canvas.create_window(640, 300, window=start_button)
        self.canvas.create_window(640, 400, window=stats_button)
        self.canvas.create_window(640, 500, window=quit_button)

    def open_stage_selection(self):
        pygame.mixer.music.stop()
        self.withdraw()
        stage_selection_window = StageSelection(self)
        self.wait_window(stage_selection_window)
        self.deiconify()
        if not stage_selection_window.started_game:
            pygame.mixer.music.play(-1)

class StageSelection(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Starry Night - Stage Selection")
        self.geometry("1280x720")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.go_back)

        self.sfx_path = "sfx/menu"
        self.sounds = parent.sounds
        self.started_game = False

        try:
            bg_image = Image.open("bg.png")
            self.bg_photo = ImageTk.PhotoImage(bg_image)
        except FileNotFoundError:
            self.bg_photo = None
            print("Warning: bg.png not found.")

        self.canvas = tk.Canvas(self, width=1280, height=720)
        self.canvas.pack(fill="both", expand=True)
        if self.bg_photo:
            self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

        self.init_ui()

    def play_sound(self, sound_key):
        sound = self.sounds.get(sound_key)
        if sound:
            sound.play()

    def init_ui(self):
        title_label = tk.Label(self, text="Select Stage", font=('Small Fonts', 58, "bold"), bg="#000000", fg="white")

        s1_button = tk.Button(self, text="Visor", font=('Small Fonts', 24), width=30,
                              command=lambda: [self.play_sound("click"), self.start_game(1)])
        s2_button = tk.Button(self, text="Dunky", font=('Small Fonts', 24), width=30,
                              command=lambda: [self.play_sound("click"), self.start_game(2)])
        stats_button = tk.Button(self, text="Statistic", font=('Small Fonts', 24), width=30,
                                 command=lambda: [self.play_sound("click"), self.parent.run_script("statistic.py")])
        back_button = tk.Button(self, text="Back to Main Menu", font=('Small Fonts', 24), width=30,
                                command=lambda: [self.play_sound("click"), self.go_back()])

        self.canvas.create_window(640, 120, window=title_label)
        self.canvas.create_window(640, 260, window=s1_button)
        self.canvas.create_window(640, 340, window=s2_button)
        self.canvas.create_window(640, 420, window=stats_button)
        self.canvas.create_window(640, 500, window=back_button)

    def start_game(self, lvl):
        self.started_game = True
        self.parent.run_script("combat_turn_based.py", lvl)
        self.destroy()

    def go_back(self):
        pygame.mixer.music.stop()
        self.destroy()

if __name__ == "__main__":
    app = StarryNightMainMenu()
    app.mainloop()