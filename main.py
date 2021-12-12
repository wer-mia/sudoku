from setup.setup import Grid
from s_input import s_string
from copy import deepcopy

g = Grid()

cells = [r*10+c for r in range(1, 10) for c in range(1, 10)]
values = list(map(int, s_string))

for cell, value in zip(cells, values):
    if value != 0:
        g.input_value(g.cells[cell], value)

print(g)

g.scan_grid()

if not g.is_solved():
    h = deepcopy(g)
    for c in h.cells.values():
        if len(c.options) == 1:
            c.options = set()
    print(h)
    f = deepcopy(g)
    for c in f.cells.values():
        if len(c.options) != 1:
            c.options = set()
    print(f)
