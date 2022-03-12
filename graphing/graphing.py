from ursina import *

app = Ursina()

class Grid3D(Entity):
    def __init__(self, x_lines, y_lines, z_lines, **kwargs):
        super().init(**kwargs)

def update():
    print(mouse.world_point, mouse.world_normal)
    
def display_information():
    line = Entity(model = "line", position = (mouse.world_point), scale = 100, )

grids = [
    Entity(model = Grid(10, 10), scale = 10, color = color.rgb(255, 0, 0), position = (2.5, 2.5, -2.5)),
    Entity(model = Grid(10, 10), scale = 10, color = color.rgb(0, 255, 0), position = (7.5, 2.5, 2.5), rotation_y = 90),
    Entity(model = Grid(10, 10), scale = 10, color = color.rgb(0, 0, 255), position = (2.5, -2.5, 2.5), rotation_y = 90, rotation_x = 90)
]

for grid in grids:
    smaller_grid = duplicate(grid)
    smaller_grid.model = Grid(10 * 4, 10 * 4)


sphere = Entity(model = "sphere", position = (2.5, 2.5, 2.5), scale = 2.5, color = color.rgb(0, 0, 0), collider = "sphere", on_click = display_information)

EditorCamera()
app.run()

"""r = 8
for i in range(1, r):
    t = i/r
    s = 4*i
    print(s)
    grid = Entity(model=Grid(s,s), scale=s, color=color.color(0,0,.8,lerp(.8,0,t)), rotation_x=90, y=i/1000)
    subgrid = duplicate(grid)
    subgrid.model = Grid(s*4, s*4)
    subgrid.color = color.color(0,0,.4,lerp(.8,0,t))
    EditorCamera()"""