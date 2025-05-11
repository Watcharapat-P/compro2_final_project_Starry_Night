from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import ast
import random
import tkinter as tk
import os

import pygame

class StatisticWindow(tk.Tk):
    def __init__(self, previous_window=None):
        super().__init__()
        self.title("Combat Statistics")
        self.geometry("1280x720")
        self.resizable(False, False)
        self.previous_window = previous_window
        if self.previous_window:
            self.previous_window.destroy()
        self.canvas_widget = None
        self.canvas_moveset_widget = None
        self.canvas_enemy_widget = None
        self.selected_graph_type = tk.StringVar()
        self.char_colors = {}
        self.init_ui()

    def init_ui(self):
        csv_file = "combat_log.csv"
        if not os.path.exists(csv_file):
            tk.messagebox.showerror("Error", f"Could not find {csv_file}. Please play some games to generate data.")
            self.destroy()
            return

        try:
            self.df = pd.read_csv(csv_file)
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error reading {csv_file}: {e}")
            self.destroy()
            return

        self.stat_options = ["Damage Dealt", "Healing Done", "Damage Mitigated"]
        self.selected_stat = tk.StringVar(self)
        self.selected_stat.set(self.stat_options[0])

        self.char_options = self.df["Name"].unique().tolist()
        self.selected_char = tk.StringVar(self)
        self.selected_char.set(self.char_options[0])

        for char in self.char_options:
            self.char_colors[char] = "#{:06x}".format(random.randint(0, 0xFFFFFF))

        self.graph_types = ["Statistic", "Moveset", "Enemy", "Table"]
        self.selected_graph_type.set(self.graph_types[0])

        dropdown_frame = ttk.Frame(self)
        dropdown_frame.pack(pady=20)

        char_label = ttk.Label(dropdown_frame, text="Select Character:")
        char_label.pack(side=tk.LEFT, padx=10)
        char_dropdown = ttk.Combobox(dropdown_frame, textvariable=self.selected_char,
                                     values=self.char_options, state="readonly")
        char_dropdown.pack(side=tk.LEFT, padx=10)
        char_dropdown.bind("<<ComboboxSelected>>", self.update_graph)

        stat_label = ttk.Label(dropdown_frame, text="Select Statistic:")
        stat_label.pack(side=tk.LEFT, padx=10)
        stat_dropdown = ttk.Combobox(dropdown_frame, textvariable=self.selected_stat,
                                     values=self.stat_options, state="readonly")
        stat_dropdown.pack(side=tk.LEFT, padx=10)
        stat_dropdown.bind("<<ComboboxSelected>>", self.update_graph)

        graph_type_label = ttk.Label(dropdown_frame, text="Select Graph Type:")
        graph_type_label.pack(side=tk.LEFT, padx=10)
        graph_type_dropdown = ttk.Combobox(dropdown_frame, textvariable=self.selected_graph_type,
                                           values=self.graph_types, state="readonly")
        graph_type_dropdown.pack(side=tk.LEFT, padx=10)
        graph_type_dropdown.bind("<<ComboboxSelected>>", self.update_graph)

        self.graph_frame = ttk.Frame(self)
        self.graph_frame.pack(fill=tk.BOTH, expand=True)

        self.moveset_graph_frame = ttk.Frame(self)
        self.moveset_graph_frame.pack(fill=tk.BOTH, expand=True)
        self.moveset_graph_frame.pack_forget()

        self.enemy_graph_frame = ttk.Frame(self)
        self.enemy_graph_frame.pack(fill=tk.BOTH, expand=True)
        self.enemy_graph_frame.pack_forget()

        self.table_frame = ttk.Frame(self)
        self.table_frame.pack(fill=tk.BOTH, expand=True)
        self.table_frame.pack_forget()

        self.back_button = ttk.Button(self, text="Back to Main Menu", command=self.back_to_main_menu)
        self.back_button.pack(anchor=tk.NE, padx=10, pady=10)

        self.update_graph()

    def update_graph(self, event=None):
        plt.clf()

        selected_stat = self.selected_stat.get()
        selected_char = self.selected_char.get()
        selected_graph_type = self.selected_graph_type.get()

        self.graph_frame.pack_forget()
        self.moveset_graph_frame.pack_forget()
        self.enemy_graph_frame.pack_forget()
        self.table_frame.pack_forget()

        if selected_graph_type == "Statistic":
            self.show_statistic_graph(selected_char, selected_stat)
            self.graph_frame.pack(fill=tk.BOTH, expand=True)
        elif selected_graph_type == "Moveset":
            self.update_moveset_graph(selected_char)
            self.moveset_graph_frame.pack(fill=tk.BOTH, expand=True)
        elif selected_graph_type == "Enemy":
            self.update_enemy_pie_chart(selected_char)
            self.enemy_graph_frame.pack(fill=tk.BOTH, expand=True)
        elif selected_graph_type == "Table":
            self.update_table_view(selected_char)
            self.table_frame.pack(fill=tk.BOTH, expand=True)

    def show_statistic_graph(self, selected_char, selected_stat):
        char_data = self.df[self.df["Name"] == selected_char]
        color = self.char_colors.get(selected_char, 'gray')

        plt.plot(range(len(char_data)), char_data[selected_stat], marker='o', color=color, label=selected_char)
        plt.title(f"{selected_char}: {selected_stat} Over Battles")
        plt.xlabel("Battle Number")
        plt.ylabel(selected_stat)
        plt.grid(True)
        plt.legend()

        canvas = FigureCanvasTkAgg(plt.gcf(), master=self.graph_frame)
        canvas.draw()
        canvas_widget = canvas.get_tk_widget()

        if self.canvas_widget:
            self.canvas_widget.destroy()

        self.canvas_widget = canvas_widget
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
        self.canvas_widget.configure(background="white")

    def update_moveset_graph(self, selected_char):
        plt.figure(figsize=(6, 4))
        moveset_data = self.df[self.df["Name"] == selected_char]
        all_moves = []
        for moveset_str in moveset_data["Movesets"]:
            try:
                moveset = ast.literal_eval(moveset_str)
                all_moves.extend(moveset)
            except (ValueError, SyntaxError) as e:
                print(f"Error parsing moveset string: {moveset_str}. Skipping. Error: {e}")
                continue

        move_counts = pd.Series(all_moves).value_counts()
        move_types = move_counts.index.tolist()
        counts = move_counts.tolist()
        color = self.char_colors.get(selected_char, 'gray')

        plt.bar(move_types, counts, color=color, label=selected_char)
        plt.title(f"{selected_char} Moveset Distribution")
        plt.xlabel("Move Type")
        plt.ylabel("Frequency")
        plt.grid(axis='y')
        plt.legend()

        canvas_moveset = FigureCanvasTkAgg(plt.gcf(), master=self.moveset_graph_frame)
        canvas_moveset.draw()
        canvas_moveset_widget = canvas_moveset.get_tk_widget()

        if self.canvas_moveset_widget:
            self.canvas_moveset_widget.destroy()

        self.canvas_moveset_widget = canvas_moveset_widget
        self.canvas_moveset_widget.pack(fill=tk.BOTH, expand=True)
        self.canvas_moveset_widget.configure(background="white")

    def update_enemy_pie_chart(self, selected_char):
        plt.figure(figsize=(6, 4))
        enemy_data = self.df[self.df["Name"] == selected_char]
        enemy_names = []
        for name in enemy_data["Name"]:
            if name == "Meepo":
                enemy_names.append("Visor")
                enemy_names.append("Dunky")
            elif name != "Meepo":
                enemy_names.append("Meepo")
        enemy_counts = pd.Series(enemy_names).value_counts()
        labels = enemy_counts.index.tolist()
        counts = enemy_counts.tolist()
        colors = [self.char_colors.get(label, 'gray') for label in labels]

        plt.pie(counts, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
        plt.title(f"{selected_char} Enemy Encounters")
        plt.legend()

        canvas_enemy = FigureCanvasTkAgg(plt.gcf(), master=self.enemy_graph_frame)
        canvas_enemy.draw()
        canvas_enemy_widget = canvas_enemy.get_tk_widget()

        if self.canvas_enemy_widget:
            self.canvas_enemy_widget.destroy()

        self.canvas_enemy_widget = canvas_enemy_widget
        self.canvas_enemy_widget.pack(fill=tk.BOTH, expand=True)
        self.canvas_enemy_widget.configure(background="white")

    def update_table_view(self, selected_char):
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        moveset_data = self.df[self.df["Name"] == selected_char]
        all_moves = []
        for moveset_str in moveset_data["Movesets"]:
            try:
                moveset = ast.literal_eval(moveset_str)
                all_moves.extend(moveset)
            except (ValueError, SyntaxError) as e:
                print(f"Error parsing moveset string: {moveset_str}. Skipping. Error: {e}")
                continue

        move_counts = pd.Series(all_moves).value_counts().reset_index()
        move_counts.columns = ["Move", "Frequency"]

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background="#f0f0f0",
                        foreground="black",
                        rowheight=28,
                        fieldbackground="#f0f0f0",
                        font=('Segoe UI', 12))
        style.configure("Treeview.Heading",
                        background="#005f99",
                        foreground="white",
                        font=('Segoe UI', 12, 'bold'))
        style.map("Treeview", background=[('selected', '#3399ff')])

        table = ttk.Treeview(self.table_frame, columns=("Move", "Frequency"), show="headings", selectmode="browse")
        table.heading("Move", text="Move", anchor="center")
        table.heading("Frequency", text="Frequency", anchor="center")
        table.column("Move", anchor="center", width=200)
        table.column("Frequency", anchor="center", width=150)

        table.tag_configure('evenrow', background="#e6f2ff")
        table.tag_configure('oddrow', background="#ffffff")
        table.tag_configure('highlight', background="#ffdf80", font=('Segoe UI', 12, 'bold'))

        for index, row in move_counts.iterrows():
            tag = 'evenrow' if index % 2 == 0 else 'oddrow'
            table.insert("", "end", values=(row["Move"], row["Frequency"]), tags=(tag,))

        table.insert("", "end", values=("", ""))

        top_move = move_counts.iloc[0]
        table.insert("", "end",
                     values=(f"Most Used: {top_move['Move']}", top_move["Frequency"]),
                     tags=("highlight",))

        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=table.yview)
        table.configure(yscrollcommand=scrollbar.set)

        table.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

    def back_to_main_menu(self):
        self.destroy()


if __name__ == "__main__":
    app = StatisticWindow()
    app.mainloop()
