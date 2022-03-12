from ursina import *
from random import randint
from math import pi, sqrt

class Sphere(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.time = 0
        self.constant_of_restituion = 0.7
        self.air_mass_density = 1.125
        self.bouncing = False
        
        self.max_height = abs((self.world_position[1] + self.world_scale_y / 2) - abs(ground.world_scale_y / 2 + ground.world_position[1]))
        self.mass = self.world_scale_z ** 3 * 4/3 * pi 


    def get_velocity(self) -> int:
        #   f = ma, therefore a = m/f where f = force, m = mass, a = acceleration
        #   f(air) = -cv**2 where c = force constant, v = velocity of object and - means opposite direction.
        #   c = f(air) / v ** 2 with no negative because we're not calculating an opposite force direction
        
        # Also using the formula of air resistance = ((air density) * (drag) * (cross sectional area)) / 2)* velocity **2
        #   https://softschools.com/formulas/physics/air_resistance_formula/85/

        # The general idea is to find the resultant force after accounting for acceleration and mass and air resistance and then
        # finding the acceleration of the overall speed and then having an attribute which'll be added to.

        # CALCULATING AIR RESISTANCE
        self.cross_sectional_area = self.world_scale_z ** 2 * pi
        self.air_resistance = (self.air_mass_density * self.cross_sectional_area / 2) * self.velocity ** 2

        # FINDING ACCELERATION
        self.resultant_force = self.mass * 9.8 - self.air_resistance    # ASSUMING SPHERE IS ALWAYS FALLING.
        self.velocity += (self.mass / self.resultant_force)             # ADDING THE ACCELERATION

        return self.velocity

    
    def get_bounce_time(self) -> int:
        self.bouncing = True
        # https://www.physicsforums.com/threads/bouncing-ball-equation.403229/
        # Essentially, assume that all the energy has been fully converted to a kinetic store from a 
        # gravitational potential store (negative because we're going in opposite direction) and multiply
        # by a coefficient of restitution. 
        # We keep increasing the height until we have reached the final height deduced by subbing in the kinetic
        # energy equation into the potential energy equation and solving for h which gives us the 
        #                                   h = v**2 / 2g
        # Because of the fact that the rebound velocity is going to change, assuming no drag therefore it'll change instanteously,
        # the kinetic energy is going to change and the change in energy is simply calculated by recalculating the kinetic energy
        # and then applying that onto the new amx_height which'll be using the new rebound_velocity as well as the potential energy.
        
        self.velocity = sqrt(2 * 9.8 * self.max_height) # CALCULATED BY SETTING KINETIC ENERGY EQUAL TO GPE AND SOLVING FOR V

        if self.velocity != 0:
            rebound_velocity = self.velocity * self.constant_of_restituion * -1
            potential_energy = 1/2 * self.mass * rebound_velocity ** 2

            return abs(self.max_height / rebound_velocity) # RETURNING ABSOLUTE BECAUSE ATTEMPTING TO FIND TIME RATHER THAN A RESULTANT FORCE.
        
        return 0

app = Ursina()

# DEFAULT RADIUS (SIDE LENGTH) IS AN OUTER SHAPE OF 10MM AND THEN AN INNER SHAPE OF 7.5MM
radius_multiplier = randint(1, 5)

# Random position is based on the radius subtract the scale_x and scale_y, this essentially ensures that the inner or outer radii spawn outside the boundary of the box.
cuboidal_box = Entity(model = "square.obj", color = color.azure, scale = (5, 5, 5), position = (randint(-50, 50), 75, randint(-50, 50)), rotation_x = 90, collider = "box")
cylindrical_box = Entity(model = "circle.obj", color = color.pink, scale = (5, 5, 5), position = (randint(-50, 50), 75, randint(-50, 50)), rotation_x = 90, collider = "box")

cuboid_count = Text("Cube: 0", position = (-.5, -.375), background = True, color = color.azure)
cylinder_count = Text("Cylinder: 0", position = (.5, -.375), background = True, color = color.pink)

spheres = []
ground = Entity(model = "cube", scale = (200, 50, 200), position = (0, 0, 0), color = color.white,  collider = "box")


def update():
    global cuboid_count, cylinder_count
    if cylindrical_box.intersects(cuboidal_box):
        cuboidal_box.world_position = (randint(-50, 50), 75, randint(-50, 50))

    for index, sphere in enumerate(spheres):
        if sphere.intersects(cuboidal_box):
            destroy(sphere)
            spheres.pop(index)
            cuboid_count.text = f'Cube: {str(int("".join(cuboid_count.text.split(":")).split(" ")[-1]) + 1)}'
        elif sphere.intersects(cylindrical_box):
            destroy(sphere)
            spheres.pop(index)
            cylinder_count.text = f'Cylinder: {str(int("".join(cylinder_count.text.split(":")).split(" ")[-1]) + 1)}'


def input(key):
    if key == "r":
        for sphere in spheres:
            destroy(sphere)

        spheres.clear()

    elif key == "c":
        new_sphere = Sphere(model = "sphere", scale = (10, 10, 10), color = color.orange, position = (randint(-100, 100), randint(200, 700), randint(-100, 100)), collider = "sphere")
        spheres.append(new_sphere)

        # Animating with a distance of the relative position subtract the scale (because the scale explodes from the origin of (0, 0, 0) and therefore must be
        # accounted for.).
        new_sphere.animate_y(-1 * (new_sphere.get_position(relative_to = ground)[1] - ground.world_scale_y) - new_sphere.world_scale_y, duration = new_sphere.get_bounce_time(), curve = curve.out_bounce)


EditorCamera()
app.run()
