from collections import Counter
from itertools import combinations


class Cell:
    def __init__(self, row, col, box):
        self.row = row
        self.col = col
        self.box = box
        self.id = row * 10 + col
        self.options = set(range(1, 10))

    def __repr__(self):
        return f'r{self.row}c{self.col}'

    def get_subgrid(self, subgrid):
        return eval(f'self.{subgrid}')


class Row:
    def __init__(self, i):
        self.i = i
        self.cells = []

    def __repr__(self):
        return f'r{self.i}'

    def add_cell(self, x):
        self.cells.append(x)


class Col:
    def __init__(self, i):
        self.i = i
        self.cells = []

    def __repr__(self):
        return f'c{self.i}'

    def add_cell(self, x):
        self.cells.append(x)


class Box:
    def __init__(self, i):
        self.i = i
        self.cells = []

    def __repr__(self):
        return f'b{self.i}'

    def add_cell(self, x):
        self.cells.append(x)


class Grid:
    """useful scripts:
        for r in g.rows.values():
            print(r, [g.cells[x] for x in r.cells])
        ... because row cells is only list of pointers, the actual cell objects are in grid.cells
    """
    def __init__(self, size=9):
        self.rows = {i: Row(i) for i in range(1, size+1)}
        self.cols = {i: Col(i) for i in range(1, size+1)}
        self.boxes = {i: Box(i) for i in range(1, size+1)}
        self.cells = {}
        for r in self.rows:
            for c in self.cols:
                i = r*10+c
                self.rows[r].cells.append(i)
                self.cols[c].cells.append(i)
                b = 0
                box_list = [[a, b] for a in range(3, 10, 3) for b in range(3, 10, 3)]
                for j, bl in enumerate(box_list):
                    if r <= bl[0] and c <= bl[1]:
                        b = j+1
                        break
                if b == 0:
                    raise AttributeError('Box 0 found')
                self.boxes[b].cells.append(i)
                self.cells[i] = Cell(r, c, b)
        self.subgrid_types = [['row', 'rows'], ['col', 'cols'], ['box', 'boxes']]
        self.is_changed = False

    def __repr__(self):
        lines = ['']
        for o in range(3):  # group of rows level
            for n in range(1, 4):  # row level
                r = n + o*3
                for m in range(3):  # group of values level (123, 456, 789)
                    s = ''
                    for k in range(3):  # group of columns level (  |  |  ||  |  |  ||  |  |  )
                        for j in range(1, 4):  # column level (  |  |  )
                            c = j + 3*k
                            for i in range(1, 4):  # value level (123)
                                x = r*10+c
                                value = i + 3*m
                                if value in self.cells[x].options:
                                    s += str(value)
                                else:
                                    s += ' '
                            if j < 3:
                                s += ' | '
                        if k < 2:
                            s += '  ||  '
                    lines.append(s)
                if n < 3:
                    lines.append('----------------------------------------------------------')
            if o < 2:
                lines.append('==========================================================')
        lines.append('')
        return '\n'.join(lines)

    def is_solved(self):
        return max([len(self.cells[c].options) for c in self.cells]) == 1

    def get_subgrid(self, subgrid):
        return eval(f'self.{subgrid}')

    def input_value(self, cell, value):
        c = self.cells[cell]
        print(f'{c}: setting value to {value}')
        c.options = {value}
        self.check_subgrids(c)

    def check_subgrids(self, cell):
        value_set = cell.options
        for sg in self.subgrid_types:
            cell_subgrid = cell.get_subgrid(sg[0])
            grid_subgrid = self.get_subgrid(sg[1])[cell_subgrid]
            print(f' Checking {sg[0]} {grid_subgrid}...', end='')
            cells_in_subgrid = [self.cells[c] for c in grid_subgrid.cells]
            if len(value_set) == 1:
                for c in cells_in_subgrid:
                    if c.options != cell.options \
                            and c.options.intersection(value_set):
                        print(f'\n{c}: limiting option from {c.options} to {c.options - value_set} because {value_set} '
                              f'in {cell}', end='')
                        c.options -= value_set
                        self.check_subgrids(c)
            else:
                self.check_n_tuples(cell, cells_in_subgrid, grid_subgrid)

    def check_n_tuples(self, cell, cells_in_subgrid, grid_subgrid):
        relevant_cells = [c for c in cells_in_subgrid if len(c.options) > 1]  # remove singles
        value_set = cell.options
        the_set = []
        the_rest = []
        for c in relevant_cells:
            if c.options == value_set:
                the_set.append(c)
            else:
                the_rest.append(c)
        if len(the_set) == len(value_set) and the_rest:
            the_rest_values = the_rest[0].options.union(*[the_rest[i].options for i in range(1, len(the_rest))])
            if the_rest_values.intersection(value_set):
                for c in the_rest:
                    if c.options.intersection(value_set):
                        print(f'\n{c}: limiting option from {c.options} to {c.options - value_set} because set '
                              f'{value_set} in {grid_subgrid}', end='')
                        c.options -= value_set
                        self.check_subgrids(c)

    def scan_grid(self):
        for sg in self.subgrid_types:
            for i in range(1, 10):
                grid_subgrid = self.get_subgrid(sg[1])[i]
                print(f' Checking {sg[0]} {grid_subgrid}...', end='')
                cells_in_subgrid = [self.cells[c] for c in grid_subgrid.cells]
                self.check_close_n_tuples(cells_in_subgrid, grid_subgrid)

    def check_hidden_singles(self):
        pass  # todo

    def check_close_n_tuples(self, cells_in_subgrid, grid_subgrid):
        relevant_cells = [c for c in cells_in_subgrid if len(c.options) > 1]  # remove singles
        if len(relevant_cells) > 3:  # in lower count close n-tuples cannot happen
            sets_counter = Counter([frozenset(c.options) for c in relevant_cells])
            # remove true n-tuples
            for s in sets_counter:
                if len(s) == sets_counter[s]:
                    relevant_cells = [c for c in relevant_cells if c.options != s]
        if len(relevant_cells) > 3:
            remaining_digits = relevant_cells[0].options.union(*[relevant_cells[i].options for i in
                                                                 range(1, len(relevant_cells))])
            sets_counter = Counter([frozenset(c.options) for c in relevant_cells])
            close_n_tuples_counter = Counter()
            for i in range(3, len(remaining_digits)):
                for combo in combinations(remaining_digits, i):
                    for s in sets_counter:
                        if s.issubset(combo):
                            if frozenset(combo) not in close_n_tuples_counter:
                                close_n_tuples_counter[frozenset(combo)] = 0
                            close_n_tuples_counter[frozenset(combo)] += 1
            close_n_tuple = None
            # select just one close n-tuple
            for nt in close_n_tuples_counter:
                if len(nt) == close_n_tuples_counter[nt]:
                    close_n_tuple = nt
                    break
            if close_n_tuple:
                for c in relevant_cells:
                    if not c.options.issubset(nt) and c.options.intersection(nt):
                        print(f'\n{c}: limiting option from {c.options} to {c.options - nt} because set '
                              f'{nt} in {grid_subgrid}', end='')
                        c.options -= nt
                        self.is_changed = True
                        self.check_subgrids(c)
