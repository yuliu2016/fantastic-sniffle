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
Pseudocode!!!

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

Sensor = namedtuple("Sensor", "activate read deactivate")
Location = namedtuple("Location", "x y z")


def dispense_container(container_id):
    material, mass, target_bin = my_table.container_properties(container_id)
    my_table.dispense_container()
    return material, mass, target_bin

pickup_location = Location(0, 0, 0)

def load_container():
    pass

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

bot.read_green_color_sensor()
##---------------------------------------------------------------------------------------
## STUDENT CODE ENDS
##---------------------------------------------------------------------------------------
update_thread = repeating_timer(2,update_sim)
