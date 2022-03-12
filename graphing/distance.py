from ursina import *

def update():
    print(mouse.hovered_entity, mouse.world_point)

def input(key):
    if key == "d":
        Entity(model = Mesh(vertices = [sphere.world_position, cube.world_position], mode = "line"))

app = Ursina()

window.exit_button.enabled = False
window.borderless = True

sphere = Entity(model = "sphere", scale = (1, 1, 1), position = (10, 0, 0), collider = "sphere")
cube = Entity(model = "cube", scale = (1, 1, 1), position = (-10, 0, 0), collider = "box")

EditorCamera()
app.run()