from pickle import TRUE
from ursina import *
from random import randint
from math import pi, sqrt

app = Ursina()

window.borderless = False
window.fps_counter.visible = True
window.exit_button.enabled = False

# DEFAULT RADIUS (SIDE LENGTH) IS AN OUTER SHAPE OF 10MM AND THEN AN INNER SHAPE OF 7.5MM AND HEIGHT OF 10MM
height = 10
inner_diameter = 7.5
outer_diameter = 10
scale_factor = 5

ground = Entity(model = "cube", scale = (200, 50, 200), position = (0, 0, 0), origin = (-.5, 0, -.5), color = color.white,  collider = "box")
spheres = []

class Sphere(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.time = 0
        self.constant_of_restituion = 0.7
        self.air_mass_density = 1.125
        self.bouncing = False
        self.counted = False
        
        self.max_height = abs((self.world_position[1] + self.world_scale_y / 2) - abs(ground.world_scale_y / 2 + ground.world_position[1]))
        self.mass = self.world_scale_z ** 3 * 4/3 * pi 


    def check_boundary(self, box: Entity):
        # Checking whether or not a sphere is inside a certain boundary of a box.
        # This is done by checking the position of a sphere (plus its scale) and checking if it's inside 
        # a certain range which will be the box's current world position for both axes and then the inner radius 
        # plus or minus.

        # self.world_position[0] ub

        """
        PREV CODE
        x_axis_positive_boundary = box.world_position[0] + inner_diameter / 2 * box.world_scale_x <= self.world_position[0] <= box.world_position[0] + outer_diameter / 2 * box.world_scale_x
        x_axis_negative_boundary = box.world_position[0] - inner_diameter / 2 * box.world_scale_x <= self.world_position[0] <= box.world_position[0] - outer_diameter / 2 * box.world_scale_x

        z_axis_positive_boundary = box.world_position[2] + inner_diameter / 2 * box.world_scale_x <= self.world_position[2] <= box.world_position[2] + outer_diameter / 2 * box.world_scale_x
        z_axis_negative_boundary = box.world_position[2] - inner_diameter / 2 * box.world_scale_x <= self.world_position[2] <= box.world_position[2] - outer_diameter / 2 * box.world_scale_x

        if (x_axis_positive_boundary or x_axis_negative_boundary) and (z_axis_positive_boundary or z_axis_negative_boundary):
            return True
        else:
            return False"""

        # The starting position of the box starts from the further z, middle x values.
        # So to account for this, drawing a circle or square interval around the center
        # regardless of y value to account for the type of bounce that may occur currently
        # as a result of disregarding the current physics behind this (only if a tolerance
        # around the center is inside the boundary will it hit the boundary)
        center = box.world_position - outer_diameter
        tolerance = self.world_scale_y * 0.25

        x_axis_positive_boundary = center + inner_diameter / 2 * box.world_scale_x <= tolerance + self.world_position[0] <= center + outer_diameter * box.world_scale_x
        x_axis_negative_boundary = center - inner_diameter / 2 * box.world_scale_x <= tolerance + self.world_position[0] <= center - outer_diameter * box.world_scale_x

        z_axis_positive_boundary = center + inner_diameter / 2 * box.world_scale_z <= tolerance + self.world_position[0] <= center + outer_diameter * box.world_scale_x
        z_axis_negative_boundary = center - inner_diameter / 2 * box.world_scale_z <= tolerance + self.world_position[0] <= center - outer_diameter * box.world_scale_x

        # Checking for every possible combination of boundary:
        #   Likely very inefficient, optimise this in another way later via abstraction.

        """
        ORIGINAL - keeping in case of something happens

        if x_axis_positive_boundary and z_axis_positive_boundary:
            return True
        
        elif x_axis_negative_boundary and z_axis_positive_boundary:
            return True

        elif x_axis_positive_boundary and z_axis_negative_boundary:
            return True

        elif x_axis_negative_boundary and z_axis_negative_boundary:
            return True

        else:
            return False

        """

        if not((x_axis_positive_boundary or x_axis_negative_boundary) and (z_axis_negative_boundary or z_axis_positive_boundary)):
            return False
        else:
            return True
        

    def get_velocity(self) -> int:
        # f = ma, therefore a = m/f where f = force, m = mass, a = acceleration
        # f(air) = -cv**2 where c = force constant, v = velocity of object and - means opposite direction.
        # c = f(air) / v ** 2 with no negative because we're not calculating an opposite force direction
        
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


# Random position is based on the radius subtract the scale_x and scale_y, this essentially ensures that the inner or outer radii spawn outside the boundary of the box.
# Multiplying scale outer radius because outer radius is 10mm and not 1mm and ensuring that the outer radius is not going over the edges of the ground.
cuboidal_box = Entity(
                model = "cuboidal_box.obj", 
                color = color.azure, 
                scale = (scale_factor, scale_factor, scale_factor),
                position = (
                    randint(outer_diameter * scale_factor, ground.world_scale_x - outer_diameter / 2 * scale_factor), 
                    ground.world_scale_y, 
                    randint(outer_diameter * scale_factor, ground.world_scale_z - outer_diameter / 2 * scale_factor)
                    ),
                collider = "box"
                )

cylindrical_box = Entity(
                    model = "cylindrical_box.obj",
                    color = color.pink, 
                    scale = (scale_factor, scale_factor, scale_factor), 
                    position = (
                        randint(outer_diameter * scale_factor, ground.world_scale_x - outer_diameter / 2 * scale_factor), 
                        ground.world_scale_y, 
                        randint(outer_diameter * scale_factor, ground.world_scale_z - outer_diameter / 2 * scale_factor)
                        ), 
                    collider = "box"
                    )

cuboid_count = Text("Cube: 0", position = (-.5, -.375), background = True, color = color.azure)
cylinder_count = Text("Cylinder: 0", position = (.5, -.375), background = True, color = color.pink)

zero_cube = Entity(model = "cube", scale = (1, 1, 1), position = (0, 0, 0), color = color.black)

def update():
    global cuboid_count, cylinder_count

    if cuboidal_box.intersects(cylindrical_box):
        cuboidal_box.world_position = (
            randint(outer_diameter * scale_factor, ground.world_scale_x - outer_diameter / 2 * scale_factor), # X AXIS
            ground.world_scale_y, # Y AXIS
            randint(outer_diameter * scale_factor, ground.world_scale_z - outer_diameter / 2 * scale_factor) # Z AXIS
            )

    # Checking for any entries within the boxes by ensuring it's within the origin of the cylinder + the scale_x * original radius
    for index, sphere in enumerate(spheres):
        # Checking that the sphere is below the height of any arbitary box (assuming cylinder and cuboid have same height)
        if not(sphere.counted) and sphere.world_position[1] <= cylindrical_box.world_position[1] * cylindrical_box.world_scale_y:
            # If a sphere is inside the x axis, or if it is inside the z axis, indexxing a world_position of (x, y, z)
            if (cuboidal_box.world_position[0] <= sphere.world_position[0] + sphere.world_scale_y <= cuboidal_box.world_position[0] + inner_diameter * cuboidal_box.world_scale_x) and (cuboidal_box.world_position[2] <= sphere.world_position[2] + sphere.world_scale_z <= cuboidal_box.world_position[2] + inner_diameter * cuboidal_box.world_scale_z):
                sphere.counted = True
                cuboid_count.text = f'Cube: {str(int("".join(cuboid_count.text.split(":")).split(" ")[-1]) + 1)}'
            elif (cylindrical_box.world_position[0] <= sphere.world_position[0] + sphere.world_scale_y <= cylindrical_box.world_position[0] + inner_diameter * cylindrical_box.world_scale_x) and (cylindrical_box.world_position[2] <= sphere.world_position[2] + sphere.world_scale_z <= cylindrical_box.world_position[2] + inner_diameter * cylindrical_box.world_scale_z):
                sphere.counted = True
                cylinder_count.text = f'Cylinder: {str(int("".join(cylinder_count.text.split(":")).split(" ")[-1]) + 1)}'

# DEBUG
def input(key):
    if key == "r":
        for sphere in spheres:
            destroy(sphere)

        spheres.clear()

    elif key == "c":
        new_sphere = Sphere(
            model = "sphere", 
            scale = (10, 10, 10), 
            color = color.orange, 
            position = (randint(0, ground.world_scale_x), randint(200, 700), randint(0, ground.world_scale_z)), 
            collider = "sphere"
            )

        spheres.append(new_sphere)

        # Checking if a sphere is inside the distance between the inner radius and the outer radius to calculate animation in either axis. (ASSUMING EQUAL SCALING)
        # Using absolute because the ground isn't centered at a corner of (0, 0, 0) and animating the bounce off the boundary rather than the ground.
        if new_sphere.check_boundary(cylindrical_box):
            new_sphere.color = color.black
            new_sphere.animate_y(-1 * (new_sphere.get_position(relative_to = cuboidal_box)[1]) - new_sphere.scale_y, duration = new_sphere.get_bounce_time(), curve = curve.out_bounce)
            # new_sphere.animate_y(-1 * (new_sphere.get_position(relative_to = cylindrical_box)[1] - height * cylindrical_box.world_scale_y) - new_sphere.world_scale_y, duration = new_sphere.get_bounce_time(), curve = curve.out_bounce)

        elif new_sphere.check_boundary(cuboidal_box):
            new_sphere.color = color.red

            # print(f"cuboidal box boundary detected. Information is:\n Sphere: {new_sphere.world_position}\n Cuboidal: {cuboidal_box.world_position}")
            new_sphere.animate_y(-1 * (new_sphere.get_position(relative_to = cylindrical_box)[1]) - new_sphere.scale_y, duration = new_sphere.get_bounce_time(), curve = curve.out_bounce)

        else:
            new_sphere.animate_y(-1 * (new_sphere.get_position(relative_to = ground)[1] - ground.world_scale_y) - new_sphere.world_scale_y, duration = new_sphere.get_bounce_time(), curve = curve.out_bounce)
            # Animating with a distance of the relative position subtract the scale (because the scale explodes from the origin of (0, 0, 0) and therefore must be
            # accounted for.). 

    elif key == "p" and mouse.hovered_entity:
        new_sphere = mouse.hovered_entity
        print(f"""
        \nInformation is: 
        Sphere: {new_sphere.world_position}
        Hovered: {mouse.world_point}

        Cylindrical: {cylindrical_box.world_position}
        Cylindrical Origin: {cylindrical_box.origin}
        Cylindrical X Axis: 
            Alerted: {cylindrical_box.world_position[0] + inner_diameter / 2 * cylindrical_box.world_scale_x <= new_sphere.world_position[0] <= cylindrical_box.world_position[0] + outer_diameter * cylindrical_box.world_scale_x}
            Inner Diameter: {cylindrical_box.world_position[0] + inner_diameter / 2 * cylindrical_box.world_scale_x}
            Cylindrical X Axis Outer Diameter: {cylindrical_box.world_position[0] + outer_diameter / 2 * cylindrical_box.world_scale_x}
        Cylindrical Z Axis:
            Alerted: {cylindrical_box.world_position[2] + inner_diameter / 2 * cylindrical_box.world_scale_z <= new_sphere.world_position[2] <= cylindrical_box.world_position[2] + outer_diameter / 2 * cylindrical_box.world_scale_z}
            Inner Diameter: {cylindrical_box.world_position[2] + inner_diameter / 2 * cylindrical_box.world_scale_z}
            Outer Diameter: {cylindrical_box.world_position[2] + outer_diameter / 2 * cylindrical_box.world_scale_z}

        Cuboidal: {cuboidal_box.world_position}
        Cuboidal Origin: {cuboidal_box.origin}
        Cuboidal X Axis: 
            Alerted: {cuboidal_box.world_position[0] + inner_diameter / 2 * cuboidal_box.world_scale_x <= new_sphere.world_position[0] <= cuboidal_box.world_position[0] + outer_diameter * cuboidal_box.world_scale_x}
            Inner Diameter: {cuboidal_box.world_position[0] + inner_diameter / 2 * cuboidal_box.world_scale_x}
            Cuboidal X Axis Outer Diameter: {cuboidal_box.world_position[0] + outer_diameter / 2 * cuboidal_box.world_scale_x}
        Cuboidal Z Axis:
            Alerted: {cuboidal_box.world_position[2] + inner_diameter / 2 * cuboidal_box.world_scale_z <= new_sphere.world_position[2] <= cuboidal_box.world_position[2] + outer_diameter / 2 * cuboidal_box.world_scale_z}
            Inner Diameter: {cuboidal_box.world_position[2] + inner_diameter / 2 * cuboidal_box.world_scale_z}
            Outer Diameter: {cuboidal_box.world_position[2] + outer_diameter / 2 * cuboidal_box.world_scale_z}
        """)

EditorCamera()
app.run()
