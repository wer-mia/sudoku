from setup.setup import Grid
from s_input import s_string

g = Grid()

cells = [r*10+c for r in range(1, 10) for c in range(1, 10)]
values = list(map(int, s_string))

for cell, value in zip(cells, values):
    if value != 0:
        g.input_value(cell, value)

print(g)

g.is_changed = True
while not g.is_solved() and g.is_changed:
    g.is_changed = False
    g.scan_grid()
    print(g)
    print(f'\nIs solved: {g.is_solved()}\n')
