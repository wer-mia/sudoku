from collections import Counter
from itertools import combinations
import inspect


class Cell:
    def __init__(self, row, col, box):
        self.row = row
        self.col = col
        self.box = box
        self.id = row.i * 10 + col.i
        self.options = set(range(1, 10))

    def __repr__(self):
        return f'{self.row}{self.col}'

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


def get_cells_without_singles_and_true_n_tuples(subgrid):
    relevant_cells = [c for c in subgrid.cells if len(c.options) > 1]  # remove singles
    if len(relevant_cells) > 3:  # in lower count hidden singles or close n-tuples cannot happen
        sets_counter = Counter([frozenset(c.options) for c in relevant_cells])
        # remove true n-tuples
        for s in sets_counter:
            if len(s) == sets_counter[s]:
                relevant_cells = [c for c in relevant_cells if c.options != s]
    return relevant_cells


def get_remaining_digits(relevant_cells):
    remaining_digits = relevant_cells[0].options.union(*[relevant_cells[i].options
                                                         for i in range(len(relevant_cells))])
    # the first union is with itself in case there is just one digit
    return remaining_digits


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
                b = 0
                box_list = [[a, b] for a in range(3, 10, 3) for b in range(3, 10, 3)]
                for j, bl in enumerate(box_list):
                    if r <= bl[0] and c <= bl[1]:
                        b = j+1
                        break
                if b == 0:
                    raise AttributeError('Box 0 found')
                i = r*10+c
                self.cells[i] = Cell(self.rows[r], self.cols[c], self.boxes[b])
                self.rows[r].cells.append(self.cells[i])
                self.cols[c].cells.append(self.cells[i])
                self.boxes[b].cells.append(self.cells[i])
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
        print(f'{cell}: setting value to {value}')
        cell.options = {value}
        self.check_subgrids(cell)

    def check_subgrids(self, cell):
        value_set = cell.options
        for sg in self.subgrid_types:
            subgrid = cell.get_subgrid(sg[0])
            print(f' Checking {sg[0]} {subgrid}...', end='')
            if len(value_set) == 1:
                for c in subgrid.cells:
                    if c.options != cell.options \
                            and c.options.intersection(value_set):
                        print(f'\n{c}: limiting option from {c.options} to {c.options - value_set} because {value_set} '
                              f'in {cell}', end='')
                        c.options -= value_set
                        self.check_subgrids(c)
            else:
                self.check_n_tuples(cell, subgrid)

    def check_n_tuples(self, cell, subgrid):
        relevant_cells = [c for c in subgrid.cells if len(c.options) > 1]  # remove singles
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
                              f'{value_set} in {subgrid}', end='')
                        c.options -= value_set
                        self.check_subgrids(c)

    def check_hidden_singles(self, subgrid):
        relevant_cells = get_cells_without_singles_and_true_n_tuples(subgrid)
        if len(relevant_cells) > 3:
            remaining_digits_counter = Counter([o for c in relevant_cells for o in c.options])
            hidden_singles = [d for d in remaining_digits_counter if remaining_digits_counter[d] == 1]
            for h in hidden_singles:
                for c in relevant_cells:
                    if h in c.options and {h} != c.options:
                        print(f'\nHidden single in {subgrid}, ', end='')
                        self.is_changed = True
                        self.input_value(c, h)

    def check_close_n_tuples(self, subgrid):
        relevant_cells = get_cells_without_singles_and_true_n_tuples(subgrid)
        close_n_tuple = None
        if len(relevant_cells) > 3:
            remaining_digits = get_remaining_digits(relevant_cells)
            sets_counter = Counter([frozenset(c.options) for c in relevant_cells])
            close_n_tuples_counter = Counter()
            for i in range(3, len(remaining_digits)):
                for combo in combinations(remaining_digits, i):
                    for s in sets_counter:
                        if s.issubset(combo):
                            if frozenset(combo) not in close_n_tuples_counter:
                                close_n_tuples_counter[frozenset(combo)] = 0
                            close_n_tuples_counter[frozenset(combo)] += 1
            # select just one close n-tuple
            for nt in close_n_tuples_counter:
                if len(nt) == close_n_tuples_counter[nt]:
                    close_n_tuple = nt
                    break
        if close_n_tuple:
            for c in relevant_cells:
                if not c.options.issubset(close_n_tuple) and c.options.intersection(close_n_tuple):
                    print(f'\n{c}: limiting option from {c.options} to {c.options - close_n_tuple} because set '
                          f'{close_n_tuple} in {subgrid}', end='')
                    c.options -= close_n_tuple
                    self.is_changed = True
                    self.check_subgrids(c)

    def check_pointing_pairs(self, box):  # they are triples in fact ;)
        relevant_cells = get_cells_without_singles_and_true_n_tuples(box)
        if relevant_cells:
            for rc in list(self.rows.values()) + list(self.cols.values()):
                overlap = [c for c in relevant_cells if c in rc.cells]
                if len(overlap) >= 2:
                    box_rest = [c for c in relevant_cells if c not in overlap]
                    rc_rest = [c for c in get_cells_without_singles_and_true_n_tuples(rc) if c not in overlap]
                    if box_rest and rc_rest:
                        for d in get_remaining_digits(overlap):
                            if d not in get_remaining_digits(box_rest) and d in get_remaining_digits(rc_rest):
                                for c in rc_rest:
                                    if d in c.options:
                                        print(f'\n{c}: limiting option from {c.options} to {c.options - {d}} because '
                                              f'pointing pair of {d} in {box}', end='')
                                        c.options -= {d}
                                        self.is_changed = True
                                        self.check_subgrids(c)
                            if d not in get_remaining_digits(rc_rest) and d in get_remaining_digits(box_rest):
                                for c in box_rest:
                                    if d in c.options:
                                        print(f'\n{c}: limiting option from {c.options} to {c.options - {d}} because '
                                              f'pointing pair of {d} in {rc}', end='')
                                        c.options -= {d}
                                        self.is_changed = True
                                        self.check_subgrids(c)

    def scan_grid(self):
        self.is_changed = True
        pipeline = [(self.check_hidden_singles, 'subgrid'),
                    (self.check_close_n_tuples, 'subgrid'),
                    (self.check_pointing_pairs, 'box')]
        while not self.is_solved() and self.is_changed:
            pipeline_copy = pipeline.copy()
            while pipeline_copy:
                check, scan_type = pipeline_copy.pop(0)
                self.is_changed = False
                print(f'\nPerforming {check.__name__}')
                if scan_type == 'subgrid':
                    for sg in self.subgrid_types:
                        for i in range(1, 10):
                            subgrid = self.get_subgrid(sg[1])[i]
                            print(f' Checking {sg[0]} {subgrid}...', end='')
                            check(subgrid)
                if scan_type == 'box':
                    for b in self.boxes.values():
                        print(f' Checking box {b}...', end='')
                        check(b)
                if self.is_changed:
                    print(self)
                    print(f'\nIs solved: {self.is_solved()}\n')
                    break  # to always perform the easier methods first after any change
