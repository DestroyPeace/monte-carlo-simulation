from ursina import *
from random import randint
from math import pi, sqrt

class Sphere(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.time = 0
        self.velocity = 0
        self.air_mass_density = 1.125
        self.constant_of_restituion = 0.5
        self.bouncing = False
        
        self.mass = self.world_scale_z ** 3 * 4/3 * pi 


    def get_velocity(self):
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

    
    def get_bounce(self):
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

        rebound_velocity = self.velocity * self.constant_of_restituion * -1
        potential_energy = 1/2 * self.mass * rebound_velocity ** 2

        max_height = rebound_velocity ** 2 / (2 * 9.8 * sqrt(2*potential_energy))
        return rebound_velocity, max_height

def update():
    # Iterating and calculating the velocity of every individual sphere by assuming gravitational constant of 9.8m/s**2
    # Checking whether or not intersection has occured with the plane (perhaps use raycasting) and then calculating bouncing.
    for index, sphere in enumerate(spheres):
        # Getting rid of any spheres that have passed the cube (temporary solution, replace with hopefully raycasting if it isn't too slow)
        if sphere.position[1] < (ground.Y + ground.world_scale_y / 2 - 20) and not(sphere.bouncing):
            destroy(sphere)
            spheres.pop(index)

        elif not(sphere.intersects(ground).hit) and not(sphere.bouncing):
            sphere.position -= (0, sphere.get_velocity(), 0)

        else:
            velocity, max_height = sphere.get_bounce()
            
            if sphere.bouncing and sphere.world_position[1] <= max_height:
                sphere.world_position[1] -= velocity



def input(key):
    if key == "r":
        for sphere in spheres:
            destroy(sphere)

        spheres.clear()
    
    # Counting number of spheres
    elif key == "c":
        new_sphere = Sphere(model = "sphere", scale = (10, 10, 10), color = color.orange, position = (randint(-100, 100), randint(0, 500), randint(-100, 100)), collider = "sphere")
        spheres.append(new_sphere)


app = Ursina()

spheres = []
sphere = Sphere(model = "sphere", scale = (2, 2, 2), position = (0, 200, 0), collider = "sphere")
spheres.append(sphere)

ground = Entity(model = "cube", scale = (200, 50, 200), position = (0, -200, 0), color = color.black,  collider = "box")

EditorCamera()
app.run()
