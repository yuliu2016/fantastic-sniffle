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
speed = 0.1  # Qbot's speed

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
Box Spacing (cm): 0
Bin01: Red (r=1, g=0, b=0), offset=60cm
Bin02: Green (r=0, g=1, b=0), offset=60cm
Bin03: Blue (r=0, g=0, b=1), offset=60cm
Bin04: White, Metallic, offset=59cm
"""

from collections import namedtuple
from typing import *

# ========== Initialize some data structures ==========

# A sensor contains three functions: an activation function,
# a read function (that takes in a bin id and duration),
# a deactivation function
Sensor = namedtuple("Sensor", "activate read deactivate")

# An XYZ location tuple (of floats)
Location = namedtuple("Location", "x y z")

# Container Properties (as determined by container_properties)
Container = namedtuple("Container", "material mass target_bin")


def dispense_container(container_id: int) -> Container:
    """Retrieve the properties of a container and dispense it """

    material, mass, target_bin = my_table.container_properties(container_id)
    my_table.dispense_container()
    container = Container(material, mass, target_bin)
    print(f"Dispensing {container}")
    return container


def check_load_container(current_containers: List[Container],
                         new_container: Container) -> bool:
    """ Check whether the QBot can hold another container,
    using a list of current containers on the QBot
    """
    if not current_containers:
        return True

    if len(current_containers) == 3:
        print("Load Container: QBot already has 3 containers")
        return False

    destination = current_containers[0].target_bin
    if destination != new_container.target_bin:
        print("Load Container: QBot's destination does not match")
        return False

    total_mass = 0
    for container in current_containers:
        total_mass += container.mass

    if total_mass + new_container.mass >= 90:
        print("Load Container: Total mass exceeds 90 grams")
        return False

    return True


# 30 degrees is enough to hold the container securely
initial_gripper = 15
arm.control_gripper(initial_gripper)

toggle_gripper = 15

pickup_location = Location(x=0.665, y=0.000, z=0.250)  # B=0, S=50, E=-35

home_location = Location(x=0.406, y=0.000, z=0.483)  # Collision avoidance

dropoff_locations = [
    Location(x=-0.145, y=-0.424, z=0.376),  # B=-115, S=5, E=10 (approx.)
    Location(x=0.000, y=-0.424, z=0.376),  # B=-90, S=5, E=10
    Location(x=0.145, y=-0.424, z=0.376)  # B=-75, S=5, E=10 (approx.)
]


def load_container(current_containers: List[Container],
                   new_container: Container) -> bool:
    """ Check whether the QBot can hold another container.
    If it can, then load that container onto the QBot. Modify
    the current_containers list in-place to keep track of state.
    """

    if not check_load_container(current_containers, new_container):
        return False

    arm.move_arm(*pickup_location)
    arm.control_gripper(toggle_gripper)
    arm.move_arm(*home_location)

    # Determine the dropoff location, index is between 0 and 2
    dropoff_location = dropoff_locations[len(current_containers)]
    arm.move_arm(*dropoff_location)

    # Backup halfway first to avoid collision
    arm.control_gripper(-toggle_gripper)
    arm.rotate_shoulder(-25)
    arm.move_arm(*home_location)

    current_containers.append(new_container)
    print("Load Container: Success")
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
    """ Move the qbot (with the containers) towards
    a target bin, using the specified sensor for that bin
    """

    # Get the target Sensor object from the dictionary
    target_sensor = qbot_sensors[target_bin]

    target_sensor.activate()

    while True:
        # Follow the yellow line
        bot.forward_velocity(bot.follow_line(0.2)[1])

        # Read sensor for 0.1 seconds, and calculate average
        data = target_sensor.read(target_bin, 0.1)
        average = sum(data) / len(data)
        if average > 4.5:  # High signal is reached
            break

    if target_sensor.read == bot.read_hall_sensor:
        # Special case for hall sensor: need to go a bit further
        bot.forward_time(0.8)

    bot.stop()
    print(f"Target Bin {target_bin} Reached")
    target_sensor.deactivate()


def control_model_actuator():
    """Use the hopper angles provided by the modelling sub-team
    to control the actuator
    """
    bot.activate_actuator()
    rotation_time, rotation = bot.process_file("hopper_angles.txt")
    elapsed = 0

    for expected_time, angle in zip(rotation_time, rotation):
        delta_t = expected_time - elapsed

        if delta_t > 1e-3:
            # Sleep for some time until expected_time, and update elapsed
            time_before_sleep = time.time()
            time.sleep(delta_t)
            elapsed += time.time() - time_before_sleep

        bot.rotate_actuator(-angle * 2)

    bot.deactivate_actuator()


def rotate_qbot_smooth(
        degree: float,
        max_velocity=1.0,  # rad/s
        max_accel=0.5,  # rad/s^2
        Ks=0.002,  # Static gain constant to overcome (static) friction
        Kv=0.005,  # Voltage gain constant to overcome dynamic drag
):
    """ Rotate the qbot a certain angle (in open-loop), but limit
    its acceleration so the containers don't fall out
    """
    direction = degree / abs(degree)
    angle = math.radians(abs(degree))

    # Apply kinematics equations to find the total required time
    v_max = min(max_velocity, math.sqrt(2 * angle * max_accel))
    t_accel = v_max / max_accel
    t_finish = t_accel + angle / v_max

    t_start = time.time()
    t_elapsed = 0
    bot.stop()

    while t_elapsed < t_finish:
        # 3 Cases: Speed ramp-up, Speed ramp-down, cruise velocity
        if t_elapsed < t_accel:
            angular_speed = t_elapsed * max_accel
        elif t_elapsed > (t_finish - t_accel):
            angular_speed = (t_finish - t_elapsed) * max_accel
        else:
            angular_speed = v_max

        # Convert to linear speed and apply gain constants
        linear_speed = angular_speed * (QBOT_DIAMETER / 2 + Kv) + Ks

        linear_speed *= direction
        bot.bot.set_velocity([linear_speed, -linear_speed])

        t_elapsed = time.time() - t_start
        time.sleep(0.05)
    bot.stop()


def deposit_container():
    """Deposit the container by rotating and travelling to
    the bin, then control it using hopper angles"""
    print("Depositing Container")

    rotate_qbot_smooth(90)
    bot.travel_forward(threshold=0.1)
    rotate_qbot_smooth(-90)

    control_model_actuator()

    bot.rotate(-90)
    bot.forward_time(time=5.4)
    bot.rotate(90)


def return_home():
    """Follow the line to return home"""
    print("Returning home")
    while True:
        lost_lines, velocity = bot.follow_line(0.3)
        if lost_lines > 2:
            break
        bot.forward_velocity(velocity)
    bot.forward_time(time=0.8)
    bot.stop()
    bot.rotate(90)
    bot.rotate(95)


def deliver_round_trip(qbot_containers: List[Container]):
    """Deliver and deposit containers in a round trip"""

    if not qbot_containers:
        return

    # Obtain the destination from the first container
    destination = qbot_containers[0].target_bin

    print(f"Delivering {len(qbot_containers)} containers to {destination}")

    transfer_container(destination)
    deposit_container()
    qbot_containers.clear()  # All containers are deposited
    return_home()
    print("Round trip delivered")


def main_loop(id_generator: Iterator[int]):
    """Main Program, accepting a generator of container IDs"""

    qbot_containers: List[Container] = []
    sorting_station_container = None

    while True:
        if sorting_station_container is None:
            # Get the next container id, or break the loop
            # if there is no more due to StopIteration;
            # then dispense and store the new container
            try:
                new_id = next(id_generator)
            except StopIteration:
                break
            sorting_station_container = dispense_container(new_id)

        # Try loading the current container onto qbot
        if load_container(qbot_containers, sorting_station_container):
            # No more container in the sorting station
            sorting_station_container = None
        else:
            # Container left in the sorting station for next trip
            deliver_round_trip(qbot_containers)

    deliver_round_trip(qbot_containers)  # final trip


def random_sequence():
    """Sorts and recycles infinite random containers"""
    main_loop(iter(lambda: random.randint(1, 6), 0))


def predetermined_sequence(*sequence):
    """Sorts and recycles with a predetermined sequence (for demos)"""
    main_loop(iter(sequence))


def user_input_sequence():
    """Allows the user to type in the sequence (for demos)"""
    main_loop(iter(lambda: int(input("(1-6 or '0' to quit) >> ")), 0))


# Comment in one of the sequences depending on the purpose
# random_sequence()
# user_input_sequence()

##---------------------------------------------------------------------------------------
## STUDENT CODE ENDS
##---------------------------------------------------------------------------------------
update_thread = repeating_timer(2, update_sim)
