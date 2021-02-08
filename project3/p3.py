import time
import random
import sys
sys.path.append('../')

from Common_Libraries.p3b_lib import *

import os
from Common_Libraries.repeating_timer_lib import repeating_timer

def update_sim():
    try:
        my_table.ping()
    except Exception as error_update_sim:
        print (error_update_sim)

### Constants
speed = 0.2 #Qbot's speed

### Initialize the QuanserSim Environment
my_table = servo_table()
arm = qarm()
arm.home()
bot = qbot(speed)

##---------------------------------------------------------------------------------------
## STUDENT CODE BEGINS
##---------------------------------------------------------------------------------------
"""
1P13 Project Three: There’s A Recyclable Among Us
Design a System for Sorting and Recycling Containers
====================================================

A computer program for transferring containers from the 
sorting station to the correct bin in the recycling station

Authors: Yu Liu, Sabiq Mahmud
"""


"""
Simulation Configuration

Table:
===========================================
Short Tower Angle (Deg): 0
Tall Tower Angle (Deg): 0
Drop Tube Angle (Deg): 180

QBot:
===========================================
QBot Orientation After Reset (Deg): 180
QBot Location Along Line After Reset (%): 0
Camera Angle (Deg): -21.5 [minimum]
Box Width (cm): 24.0
Box Length (cm): 35.5
Wall Height (cm):
    Left, Right, Back: 4.0
    Front: 11.0
    
Bins:
===========================================
Bin01: Red (r=1, g=0, b=0)
Bin02: Green (r=0, g=1, b=0)
Bin03: Blue (r=0, g=0, b=1)
Bin04: White, Metallic
"""

# =========================================

"""
High Level Pseudocode:
===========================================

Function Dispense Container
    Input  <- Container ID
    Determine Container Attributes from ID
    Dispense container in Sorting Station
    Output -> Container Attributes
End Function

Function Load Container
    Input  -> Container Attributes
    If Qbot already has 3 containers
        OR Destination is different
        OR Total mass exceeds 90 grams
            Exit the Function
    Else
        QArm picks up container from Sorting Station
        QArm drops off container onto QBot
End Function

Function Transfer Container
    Input -> Bin Number, Sensor Type
    While Sensor for Bin Number not Activated
        Move QBot forward
End Function

Function Deposit Container
    Turn QBot towards bin
    Move Qbot forward until a distance threshold
    Turn QBot to Align Hopper to Bin
    [Optional: Use File Data]
    Rotate Hopper to Deposit
    Move QBot Back to Yellow Line
End Function

Function Return Home
    While not at the end of the line
        QBot follows line in a loop
    Rotate QBot around
End Function

Program Main
    Initialize Environment and Reset
    Loop Forever
        Generate Random Container ID
        Dispense Container
        Load Container
        Transfer Container
        Deposit Container
        Return Home
    End Loop 
End Program
"""

from collections import namedtuple
from typing import List

# Initialize some data structures to make it easier
# to pass data around. A "named tuple" acts like a tuple,
# except elements can be accessed by its name in addition
# to its index

# A sensor contains three functions: an activation function,
# a read function (that takes in a bin id and duration),
# and a deactivation function
Sensor = namedtuple("Sensor", "activate read deactivate")

# An XYZ tuple (of floats)
Location = namedtuple("Location", "x y z")

# Container Properties (as determined by container_properties)
Container = namedtuple("Container", "material mass target_bin")

# Note: Some functions have type annotations; they are purely
# for readablility purposes and do not affect the program
# in any way


def dispense_container(container_id: int) -> Container:
    """
    Retrieve the properties of a container based on the ID,
    then dispense it onto the turn table

    ID specification:
        1 = non contaminated plastic
        2 = non-contaminated metal
        3 = non-contaminated paper
        4 = contaminated plastic
        5 = contaminated metal
        6 = contaminated paper

    :param container_id: a (randomized) id between 1 and 6
    :return: a Container with all the properties
    """

    # Get the container properties, and prepare to dispense
    material, mass, target_bin = my_table.container_properties(container_id)

    # Actually dispense the container (includes 1 second delay)
    my_table.dispense_container()

    return Container(material, mass, target_bin)


# Pickup location. Shoulder 50 degrees, elbow -35 degrees
pickup_location = Location(x=0.665, y=0.000, z=0.250)

# 30 degrees is enough to hold the container securely
# (for both the metal and plastic containers)
gripper_strength = 30

# The home position acts like an in-between position, so
# that the QArm doesn't hit other stuff when trying to
# move to another location
home_location = Location(x=0.406, y=0.000, z=0.483)

# There are three dropoff locations on top of the Qbot,
# allowing the Qbot to carry up to 3 containers. These
# locations assume that the Qbot is parked at 0% (home
# position) and is turned to face away from the QArm

# The locations are specified in a list, and the ordering
# in the list is such that the furthest location from
# the QArm comes first. This is to avoid knocking over
# other containers as new ones come in
dropoff_locations = [
    # Base: -90, Shoulder: 20, Elbow: -15
    Location(x=0.000, y=-0.526, z=0.426),

    # Base: -90, Shoulder: 0, Elbow: 10
    Location(x=0.000, y=-0.400, z=0.412),

    # Base: -90, Shoulder: -20, Elbow: 30
    Location(x=0.000, y=-0.279, z=0.391)
]


def load_container(current_containers: List[Container],
                   new_container: Container) -> bool:
    """
    Check whether the QBot can hold another container. If it
    can, then load that container onto the QBot. Modify the
    current_containers list in-place to keep track of state

    :param current_containers: list of current containers on the QBot
    :param new_container: the new container to be added
    :return: True if container is successfully added
    """

    if len(current_containers) == 3:
        # Already enough containers; requires a new trip
        return False

    if current_containers:
        # List is not empty; Check the first item
        destination = current_containers[0].target_bin
        if destination != new_container.target_bin:
            # A new destination requires a new trip
            return False

    total_mass = sum(cont.mass for cont in current_containers)
    new_mass = total_mass + new_container.mass

    if new_mass >= 90:  # grams
        # Maximum mass exceeded; requires a new trip
        return False

    # Now the actual container has to be loaded

    # Move to the pickup location and grab the spawned
    arm.move_arm(*pickup_location)
    arm.control_gripper(gripper_strength)

    # Determine the dropoff location
    # Index is between 0 and 2
    dropoff_index = len(current_containers)
    dropoff_location = dropoff_locations[dropoff_index]

    # First go back to home to avoid collisions
    arm.move_arm(*home_location)
    arm.move_arm(*dropoff_location)

    # Move back home
    arm.move_arm(*home_location)

    # Add current container to the list
    current_containers.append(new_container)

    # Success
    return True


qbot_sensors = {
    "red": Sensor(
        activate=lambda: bot.activate_color_sensor("red"),
        read=bot.read_red_color_sensor,
        deactivate=bot.deactivate_color_sensor
    ),
    "green": Sensor(
        activate=lambda: bot.activate_color_sensor("green"),
        read=bot.read_green_color_sensor,
        deactivate=bot.deactivate_color_sensor
    ),
    "blue": Sensor(
        activate=lambda: bot.activate_color_sensor("blue"),
        read=bot.read_blue_color_sensor,
        deactivate=bot.deactivate_color_sensor
    )
}

def transfer_container(target_bin):
    bot.read_green_color_sensor(3, 4)


def deposit_container():
    bot.rotate(90)
    bot.travel_forward(threshold=0.5)
    bot.rotate(-90)
    bot.dump()
    bot.rotate(90)
    while True:
        lost_lines, velocity = bot.follow_line(0.2)
        if lost_lines > 2:
            break
        bot.forward_velocity(velocity)
    bot.rotate(-90)

def return_home():
    while True:
        lost_lines, velocity = bot.follow_line(0.2)
        if lost_lines > 2:
            break
        bot.forward_velocity(velocity)
    bot.stop()
    bot.rotate(180)


def main():
    pass


# Call the main function to run ALL the code
main()
##---------------------------------------------------------------------------------------
## STUDENT CODE ENDS
##---------------------------------------------------------------------------------------
update_thread = repeating_timer(2,update_sim)
