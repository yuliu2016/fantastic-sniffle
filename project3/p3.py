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
        print(error_update_sim)


### Constants
speed = 0.2  # Qbot's speed

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

# =========================================

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
Box Width (cm): 40.0
Box Length (cm): 15.0
Wall Height (cm):
    Left, Front, Back: 7.0
    Right: 0.0 [for dumping]

Bins:
===========================================
Box Spacing (cm): 10
Bin01: Red (r=1, g=0, b=0), offset=60cm
Bin02: Green (r=0, g=1, b=0), offset=60cm
Bin03: Blue (r=0, g=0, b=1), offset=60cm
Bin04: White, Metallic, offset=60cm
"""

from collections import namedtuple
from typing import *

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


def dispense_container(container_id: int) -> Container:
    """
    Retrieve the properties of a container based on the ID,
    then dispense it onto the turn table, returning the
    properties as a Container object
    """
    material, mass, target_bin = my_table.container_properties(container_id)
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


def check_load_container(current_containers: List[Container],
                         new_container: Container) -> bool:
    """ Check whether the QBot can hold another container,
    using a list of current containers on the QBot
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

    # Add up all the mass for the current containers
    total_mass = sum(cont.mass for cont in current_containers)
    new_mass = total_mass + new_container.mass

    if new_mass >= 90:  # grams
        # Maximum mass exceeded; requires a new trip
        return False

    return True


def load_container(current_containers: List[Container],
                   new_container: Container) -> bool:
    """ Check whether the QBot can hold another container.
    If it can, then load that container onto the QBot. Modify
    the current_containers list in-place to keep track of state.
    """

    # First check if this container can be loaded
    if not check_load_container(current_containers, new_container):
        return False

    arm.move_arm(*pickup_location)
    arm.control_gripper(gripper_strength)

    # Determine the dropoff location
    # Index is between 0 and 2
    dropoff_index = len(current_containers)
    dropoff_location = dropoff_locations[dropoff_index]

    arm.move_arm(*home_location)

    arm.move_arm(*dropoff_location)
    arm.control_gripper(-gripper_strength)

    arm.move_arm(*home_location)

    current_containers.append(new_container)
    return True


# A dictionary of all the Sensors used for the bin
qbot_sensors = {
    "Bin01": Sensor(
        activate=lambda: bot.activate_color_sensor("red"),
        read=bot.read_red_color_sensor,
        deactivate=bot.deactivate_color_sensor),

    "Bin02": Sensor(
        activate=lambda: bot.activate_color_sensor("green"),
        read=bot.read_green_color_sensor,
        deactivate=bot.deactivate_color_sensor),

    "Bin03": Sensor(
        activate=lambda: bot.activate_color_sensor("blue"),
        read=bot.read_blue_color_sensor,
        deactivate=bot.deactivate_color_sensor),

    "Bin04": Sensor(
        activate=bot.activate_hall_sensor,
        read=bot.read_hall_sensor,
        deactivate=bot.deactivate_hall_sensor)
}


def transfer_container(target_bin: str):
    """
    Move the qbot (with the containers) towards
    a target bin
    """

    # Get the target sensor object
    target_sensor = qbot_sensors[target_bin]
    # Activate that sensor
    target_sensor.activate()

    while True:
        # Follow the yellow line
        _, velocity = bot.follow_line(0.3)
        bot.forward_velocity(velocity)

        # Read the sensor for 0.1 seconds
        data = target_sensor.read(target_bin, 0.1)

        # Calculate the average sensor signal
        avg = sum(data) / len(data)

        # Stop once the high signal is reached
        if avg > 4.5:
            bot.stop()
            break

    # Deactivate the sensor
    target_sensor.deactivate()


def dump_angle_controlled():
    """
    Us
    """
    bot.activate_actuator()
    rotation_time, rotation = bot.process_file("hopper_angles.txt")
    elapsed = 0
    for t, r in zip(rotation_time, rotation):
        delta_t = t - elapsed
        if delta_t > 1e-3:
            time_before_sleep = time.time()
            time.sleep(delta_t)
            elapsed += time.time() - time_before_sleep
        bot.rotate_actuator(-r)
    bot.deactivate_actuator()


def deposit_container():
    bot.rotate(90)
    bot.travel_forward(0.22)
    bot.rotate(-90)

    dump_angle_controlled()

    bot.rotate(-90)
    bot.forward_time(2.7)
    bot.rotate(90)


def return_home():
    """
    Follow the line to return home
    """
    while True:
        lost_lines, velocity = bot.follow_line(0.3)
        if lost_lines > 2:
            break
        bot.forward_velocity(velocity)
    bot.stop()
    bot.rotate(180)


def main_loop(id_generator: Iterator[int]):
    """Main Program"""

    # List of containers currently on the qbot
    qbot_containers: List[Container] = []

    # The state of the container on the Sorting Station
    sorting_station_container = None

    while True:

        # Generate a new container, only if there isn't one
        # already in the sorting station
        if sorting_station_container is None:
            try:
                new_id = next(id_generator)
            except StopIteration:
                break
            sorting_station_container = dispense_container(new_id)

        load_success = load_container(qbot_containers, sorting_station_container)
        if load_success:
            # Container loaded onto QBot successfully
            sorting_station_container = None

            # The infinite loop gets to run immediately
            # to attempt to load more before a trip
            continue

        # Load unsuccessful; starting the trip now
        # Note: sorting_station_container is unchanged to
        # prepare for the ~next~ trip.
        destination = qbot_containers[0].target_bin

        # Transfer the container to the bin, and return home
        transfer_container(destination)
        deposit_container()
        return_home()

        qbot_containers.clear()


def random_sequence():
    """
    Generates random containers (for program requirement)
    """
    while True:
        yield random.randint(1, 6)


def predermined_sequence():
    """
    Generates predetermined containers (for demonstrations)
    """
    yield from  [
        2, 2, 2
    ]

# Call the main function to run ALL the code
# main()
main_loop(predermined_sequence())

# todo fix tall bottle being knocked off
# todo fix metallic box
# todo comment
# todo fix return home not reaching destination

##---------------------------------------------------------------------------------------
## STUDENT CODE ENDS
##---------------------------------------------------------------------------------------
update_thread = repeating_timer(2, update_sim)
