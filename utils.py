import random
from dataclasses import dataclass, field
from typing import List, Tuple, Set
import settings

@dataclass
class Cell:
    row: int
    col: int
    has_mine: bool = False
    revealed: bool = False
    flagged: bool = False
    adjacent: int = 0

    def __repr__(self):
        return f"Cell({self.row},{self.col},mine={self.has_mine},adj={self.adjacent})"

class Board:
    def __init__(self, rows: int, cols: int, mines: int):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self._grid: List[List[Cell]] = [[Cell(r, c) for c in range(cols)] for r in range(rows)]
        self._mines_planted = False
        self.state = settings.STATE_PLAYING

    def in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < self.rows and 0 <= c < self.cols

    def neighbors(self, r: int, c: int) -> List[Tuple[int,int]]:
        n = []
        for dr in (-1,0,1):
            for dc in (-1,0,1):
                if dr == 0 and dc == 0:
                    continue
                rr, cc = r+dr, c+dc
                if self.in_bounds(rr, cc):
                    n.append((rr, cc))
        return n

    def plant_mines(self, first_click: Tuple[int,int]=None):
        # Place mines randomly but avoid the first_click cell (so first move never hits mine)
        all_positions = [(r, c) for r in range(self.rows) for c in range(self.cols)]
        if first_click and first_click in all_positions:
            all_positions.remove(first_click)
            # also remove neighbors for friendlier first click
            for (nr, nc) in self.neighbors(*first_click):
                if (nr, nc) in all_positions:
                    all_positions.remove((nr, nc))
        mines_pos = random.sample(all_positions, k=self.mines)
        for (r, c) in mines_pos:
            self._grid[r][c].has_mine = True
        # compute adjacent counts
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self._grid[r][c]
                cell.adjacent = sum(1 for (nr,nc) in self.neighbors(r,c) if self._grid[nr][nc].has_mine)
        self._mines_planted = True

    def reveal(self, r: int, c: int) -> List[Tuple[int,int]]:
        changed = []
        cell = self._grid[r][c]
        if not self._mines_planted:
            # delay planting until first reveal to guarantee safe first click
            self.plant_mines(first_click=(r,c))
        if cell.flagged or cell.revealed:
            return changed
        cell.revealed = True
        changed.append((r,c))
        if cell.has_mine:
            self.state = settings.STATE_LOST
            # reveal all mines
            for rr in range(self.rows):
                for cc in range(self.cols):
                    if self._grid[rr][cc].has_mine and not self._grid[rr][cc].revealed:
                        self._grid[rr][cc].revealed = True
                        changed.append((rr,cc))
            return changed
        # if zero adjacent, flood fill reveal neighbors
        if cell.adjacent == 0:
            stack = [(r,c)]
            visited = set(stack)
            while stack:
                cr, cc = stack.pop()
                for nr, nc in self.neighbors(cr, cc):
                    neighbor = self._grid[nr][nc]
                    if not neighbor.revealed and not neighbor.flagged:
                        neighbor.revealed = True
                        changed.append((nr,nc))
                        if neighbor.adjacent == 0 and (nr,nc) not in visited:
                            visited.add((nr,nc))
                            stack.append((nr,nc))
        # Check win: all non-mine cells revealed
        if self._check_win():
            self.state = settings.STATE_WON
            # automatically flag remaining mines
            for rr in range(self.rows):
                for cc in range(self.cols):
                    if self._grid[rr][cc].has_mine:
                        self._grid[rr][cc].flagged = True
            # add flagged mine positions to changed for UI update
            for rr in range(self.rows):
                for cc in range(self.cols):
                    if self._grid[rr][cc].flagged:
                        changed.append((rr,cc))
        return changed

    def toggle_flag(self, r: int, c: int) -> Tuple[bool, Tuple[int,int]]:
        cell = self._grid[r][c]
        if cell.revealed:
            return False, (r,c)
        cell.flagged = not cell.flagged
        return True, (r,c)

    def _check_win(self) -> bool:
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self._grid[r][c]
                if not cell.has_mine and not cell.revealed:
                    return False
        return True

    def get_cell(self, r: int, c: int) -> Cell:
        return self._grid[r][c]

    def debug_print(self):
        for r in range(self.rows):
            row_s = []
            for c in range(self.cols):
                cell = self._grid[r][c]
                if cell.has_mine:
                    row_s.append('*')
                else:
                    row_s.append(str(cell.adjacent))
            print(' '.join(row_s))

            