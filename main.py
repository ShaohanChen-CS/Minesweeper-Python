import tkinter as tk
from tkinter import messagebox
from utils import Board
from settings import DIFFICULTIES, STATE_PLAYING, STATE_LOST, STATE_WON, MINE_SYMBOL, FLAG_SYMBOL, WINDOW_PADDING
from functools import partial

class MinesweeperUI:
    def __init__(self, root, rows, cols, mines):
        self.root = root
        self.board = Board(rows, cols, mines)
        self.buttons = {}
        self.create_widgets()
        self.update_status()

    def create_widgets(self):
        top_frame = tk.Frame(self.root, padx=WINDOW_PADDING, pady=WINDOW_PADDING)
        top_frame.pack()
        self.status_label = tk.Label(top_frame, text='', font=('Arial', 12))
        self.status_label.pack(side='top', pady=(0,8))
        grid_frame = tk.Frame(top_frame)
        grid_frame.pack()
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                b = tk.Button(grid_frame, width=2, height=1, text=' ',
                              command=partial(self.on_left_click, r, c))
                b.bind('<Control-Button-1>', partial(self.on_right_click, r, c))
                b.grid(row=r, column=c)
                self.buttons[(r,c)] = b
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=(6,10))
        tk.Button(control_frame, text='Restart', command=self.restart).pack(side='left', padx=4)
        tk.Button(control_frame, text='Quit', command=self.root.quit).pack(side='left', padx=4)

    def on_left_click(self, r, c):
        if self.board.state != STATE_PLAYING:
            return
        changed = self.board.reveal(r,c)
        self.refresh_buttons(changed)
        self.update_status()
        if self.board.state == STATE_LOST:
            messagebox.showinfo('Game Over', 'You clicked a mine! Game over.')
        elif self.board.state == STATE_WON:
            messagebox.showinfo('Congratulations', 'You won!')

    def on_right_click(self, r, c, event=None):
        if self.board.state != STATE_PLAYING:
            return
        ok, pos = self.board.toggle_flag(r,c)
        if ok:
            self.refresh_buttons([pos])
        self.update_status()

    def refresh_buttons(self, changed_positions):
        for (r,c) in changed_positions:
            cell = self.board.get_cell(r,c)
            btn = self.buttons[(r,c)]
            if cell.revealed:
                if cell.has_mine:
                    btn.config(text=MINE_SYMBOL, relief='sunken', state='disabled')
                else:
                    btn.config(text=str(cell.adjacent) if cell.adjacent>0 else ' ', relief='sunken', state='disabled')
            else:
                if cell.flagged:
                    btn.config(text=FLAG_SYMBOL)
                else:
                    btn.config(text=' ')

    def update_status(self):
        flags = sum(1 for r in range(self.board.rows) for c in range(self.board.cols)
                    if self.board.get_cell(r,c).flagged)
        mines = self.board.mines
        self.status_label.config(text=f'State: {self.board.state}    Mines: {mines}    Flags: {flags}')

    def restart(self):
        self.board = Board(rows=self.board.rows, cols=self.board.cols, mines=self.board.mines)
        # reset buttons
        for (r,c), btn in self.buttons.items():
            btn.config(text=' ', relief='raised', state='normal')
        self.update_status()



root = tk.Tk()
root.title("Select Difficulty")

def start(difficulty_name):
    diff = DIFFICULTIES[difficulty_name]
    for widget in root.winfo_children():
        widget.destroy()
    root.title(f"Minesweeper - {difficulty_name}")
    MinesweeperUI(root, rows=diff["ROWS"], cols=diff["COLS"], mines=diff["MINES"])

tk.Label(root, text="Choose Difficulty:", font=("Arial",14)).pack(pady=10)
for level in DIFFICULTIES:
    tk.Button(root, text=level, width=20, command=lambda l=level: start(l)).pack(pady=5)

root.mainloop()
