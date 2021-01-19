import sys
sys.path.append('../')

from Common_Libraries.quanser_sim_lib import *

import os
from Common_Libraries.repeating_timer_lib import repeating_timer

def update_sim ():
    try:
        qbot.ping()
    except Exception as error_update_sim:
        print (error_update_sim)


QIL = postman(18001)

class qarm:

    def __init__(self):

        self.my_qarm = QArm_sim(QIL)
        self.my_qarm.set_base_color([0, 1, 0])

        self.tolerance = 0.01

        self.cage_red_small = [1, 0.5, "Small red cage"]
        self.cage_green_small = [2, 0.5, "Small green cage"]
        self.cage_blue_small = [3, 0.5, "Small blue cage"]
        self.cage_red_large = [4, 1, "Large red cage"]
        self.cage_green_large = [5, 1, "Large green cage"]
        self.cage_blue_large = [6, 1, "Large blue cage"]

        self.my_cage = genericSpawn_sim(QIL)

        self.red_autoclave = autoclave_sim(QIL, 0)
        self.green_autoclave = autoclave_sim(QIL, 1)
        self.blue_autoclave = autoclave_sim(QIL, 2)

        self.my_emg = EMG_sim(QIL)

        self.home()

        # Used to establish continuous communication

    def ping(self):
        self.my_qarm.ping()

    def effector_position(self):
        x_pos, y_pos, z_pos = self.my_qarm.qarm_forward_kinematics(self.b, self.s, self.e, self.w)
        return x_pos, y_pos, z_pos

    def home(self):

        self.my_qarm.qarm_move(0, 0, 0, 0, 0, wait = False)
        self.b, self.s, self.e, self.w, self.g = 0, 0, 0, 0, 0
        time.sleep(0.1)

    # enter a value between 1 and 6 (inclusive). 1,2,3 for small red, green and blue containers respectively,
    # and 4,5,6 for large red, green and blue containers respectively
    def spawn_cage(self, value):
        if value == 1:
            self.my_cage.spawn_with_properties(self.cage_red_small[0], self.cage_red_small[1],
                                               self.cage_red_small[2])
        elif value == 2:
            self.my_cage.spawn_with_properties(self.cage_green_small[0], self.cage_green_small[1],
                                               self.cage_green_small[2])
        elif value == 3:
            self.my_cage.spawn_with_properties(self.cage_blue_small[0], self.cage_blue_small[1],
                                               self.cage_blue_small[2])
        elif value == 4:
            self.my_cage.spawn_with_properties(self.cage_red_large[0], self.cage_red_large[1], self.cage_red_large[2])
        elif value == 5:
            self.my_cage.spawn_with_properties(self.cage_green_large[0], self.cage_green_large[1],
                                               self.cage_green_large[2])
        elif value == 6:
            self.my_cage.spawn_with_properties(self.cage_blue_large[0], self.cage_blue_large[1],
                                               self.cage_blue_large[2])
        else:
            print("Please enter a value between 1 and 6 (inclusive)")
        time.sleep(0.1)
        return value

    # Rotate Joints
    def rotate_base(self, deg):
        b = self.b + math.radians(deg)
        if abs(b) > math.radians(175):
            print("Invalid Angle. Base does not rotate beyond +/- 175 degrees")
        else:
            self.b = b
            self.my_qarm.qarm_move_base(self.b, wait = False)

    def rotate_shoulder(self, deg):
        s = self.s + math.radians(deg)
        if abs(s) > math.radians(90):
            print("Invalid Angle. Shoulder does not rotate beyond +/- 90 degrees")
        else:
            self.s = s
            self.my_qarm.qarm_move_shoulder(self.s, wait = False)

    def rotate_elbow(self, deg):
        e = self.e + math.radians(deg)
        if e > math.radians(90) or e < math.radians(-80):
            print("Invalid Angle. Elbow does not rotate beyond +90 or -80 degrees")
        else:
            self.e = e
            self.my_qarm.qarm_move_elbow(self.e, wait = False)

    def rotate_wrist(self, deg):
        w = self.w + math.radians(deg)
        if abs(w) > math.radians(170):
            print("Invalid Angle. Wrist does not rotate beyond +/- 170 degrees")
        else:
            self.w = w
        self.my_qarm.qarm_move_wrist(self.w, wait = False)

    # Control Gripper. Gripper moves between 0 - 55 degrees
    def control_gripper(self, value):
        if abs(value) <= 55 and math.degrees(self.g + math.radians(value)) >= 0 and math.degrees(
                self.g + math.radians(value)) < 56:
            self.g = self.g + math.radians(value)
            self.my_qarm.qarm_move_gripper(self.g, wait = False)
        else:
            print("Please enter a value in between +/- 55 degrees.")

    # Open / Close the Autoclave. Takes values of True = open, False = close
    def open_red_autoclave(self, value):
        self.red_autoclave.open_drawer(value)

    def open_green_autoclave(self, value):
        self.green_autoclave.open_drawer(value)

    def open_blue_autoclave(self, value):
        self.blue_autoclave.open_drawer(value)

    # EMG Sensor Readings
    def emg_left(self):
        emg_left, emg_right = self.my_emg.read_all_sensors()
        return emg_left

    def emg_right(self):
        emg_left, emg_right = self.my_emg.read_all_sensors()
        return emg_right

    # Move arm to target location based on cartesian coordinate inputs
    def move_arm(self, x, y, z):
        self.b, self.s, self.e = self.my_qarm.qarm_inverse_kinematics(x, y, z)
        self.my_qarm.qarm_move(self.b, self.s, self.e, self.w, self.g, wait = False)

arm = qarm()
qbot = QBot2e_sim(QIL)
table = rotarytable_sim(QIL)

update_thread = repeating_timer(2, update_sim)


## STUDENT CODE BEGINS
## ----------------------------------------------------------------------------------------------------------
## Example to rotate the base: arm.rotateBase(90)
from random import random

def rc():
    return [random(), random(), random()]

def spawn(c, m):
    table.spawn_single_bottle(c, m)
    time.sleep(0.5)

def spw():
    spawn(rc(), "metal")

def pid(angle):
    table.command_rel_position_pid(angle)

def enc():
    kEnc =  360/4096
    encoder = table.read_encoder()
    if not encoder:
        encoder = 0
    return int(encoder * kEnc)

def cw():
    table.rotate_clockwise(1.0)

def ccw():
    table.rotate_counterclockwise(1.0)

def st():
    table.stop_table()

def op():
    arm.control_gripper(-45)

def cl():
    arm.control_gripper(45)