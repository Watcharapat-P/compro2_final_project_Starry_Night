import tkinter as tk
import os
import subprocess
import sys
import threading


class StageSelection(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Starry Night - Stage Selection")
        self.geometry("1280x720")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.quit_game)
        self.init_ui()
        self.game_process = None

    def init_ui(self):
        title_label = tk.Label(self, text="Starry Night", font=("Times", 32, "bold"))
        title_label.pack(pady=100)

        s1_button = tk.Button(self, text="Stage 1", font=("Arial", 24), width=30, command=lambda: self.start_game(1))
        s1_button.pack(pady=10)

        s2_button = tk.Button(self, text="Stage 2", font=("Arial", 24), width=30, command=lambda: self.start_game(2))
        s2_button.pack(pady=10)

        stats_button = tk.Button(self, text="Statistic", font=("Arial", 24), width=30, command=self.stats)
        stats_button.pack(pady=10)

        quit_button = tk.Button(self, text="Back to Main Menu", font=("Arial", 24), width=30, command=self.main_menu)
        quit_button.pack(pady=10)

    def start_game(self, lvl):
        try:
            current_directory = os.path.dirname(os.path.realpath(__file__))
            game_script = os.path.join(current_directory, "combat_turn_based.py")

            if not os.path.exists(game_script):
                raise FileNotFoundError(f"Could not find {game_script}")

            def run_game():
                try:
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
        self.destroy()

    def quit_game(self):
        if self.game_process:
            self.game_process.terminate()
            self.game_process.wait()
        self.destroy()


if __name__ == "__main__":
    app = StageSelection()
    app.mainloop()