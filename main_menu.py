import tkinter as tk
import os
import subprocess
import sys
import threading

class StarryNightMainMenu(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Starry Night - Main Menu")
        self.geometry("1280x720")
        self.resizable(False, False)
        self.init_ui()
        self.game_process = None

    def init_ui(self):
        title_label = tk.Label(self, text="Starry Night", font=("Times", 32, "bold"))
        title_label.pack(pady=40)

        start_button = tk.Button(self, text="Start", font=("Arial", 14), width=15, command=self.start_game)
        start_button.pack(pady=10)

        quit_button = tk.Button(self, text="Quit", font=("Arial", 14), width=15, command=self.quit_game)
        quit_button.pack(pady=10)

    def start_game(self):
        try:
            current_directory = os.path.dirname(os.path.realpath(__file__))
            game_script = os.path.join(current_directory, "combat_turn_based.py")

            if not os.path.exists(game_script):
                raise FileNotFoundError(f"Could not find {game_script}")

            def run_game():
                try:
                    self.game_process = subprocess.Popen([sys.executable, game_script])
                    self.game_process.wait()
                except Exception as e:
                    print(f"Error running game: {e}")

            threading.Thread(target=run_game).start()

            self.destroy()

        except Exception as e:
            tk.messagebox.showerror("Error", f"Could not launch game: {e}")
            print(f"Error in start_game: {e}")

    def quit_game(self):
        if self.game_process:
            self.game_process.terminate()
            self.game_process.wait()
        self.destroy()

if __name__ == "__main__":
    app = StarryNightMainMenu()
    app.mainloop()
