from typing import *

class qarm:

    def rotate_base(self, deg: float) -> None:
        """It rotates the base joint by the number of degrees specified when the function is called.
        Function calls are relative to each other, meaning when rotating the base by 35 degrees at
        first then later by 40 degrees, the final position will be at 75 degrees and not 40 degrees with
        movement limitation of +/- 175 degrees.

        Example: The first function call rotates the base joint 56 degrees counter-clockwise and
        second function call rotates the joint 35 degrees in the clockwise direction. 
        >>> arm.rotate_base(56)
        >>> arm.rotate_base(-35)
        """
        pass

    def rotate_shoulder(self, deg: float) -> None:
        """It rotates the shoulder joint by the number of degrees specified when the function is called.
        Function calls are relative to each other, meaning when rotating the shoulder by 20 degrees
        at first then later by -15 degrees, the final position will be at 5 degrees and not -15 degrees
        with movement limitation of +/- 90 degrees.

        Example: The first line rotates the shoulder joint 45 degrees upwards while the second
        rotates it 67 degrees downwards.
        >>> arm.rotate_shoulder(-45)
        >>> arm.rotate_shoulder(67)
        """
        pass

    def rotate_elbow(self, deg: float) -> None:
        """It rotates the elbow joint by the number of degrees specified when the function is called.
        Function calls are relative to each other, meaning when rotating the elbow by 10 degrees at
        first then later by -20 degrees, the final position will be at -10 degrees and not -20 degrees
        with movement limitation of +90 degrees in the downward direction and -80 degrees in the
        upward direction.

        Example: The first line rotates the elbow joint 10 degrees upward while the second rotates it
        5 degrees downward.
        >>> arm.rotate_elbow(-10)
        >>> arm.rotate_elbow(5)
        """
        pass

    def rotate_wrist(self, deg: float) -> None:
        """It rotates the wrist joint by the number of degrees specified when the function is called.
        Function calls are relative to each other, meaning when rotating the wrist by 5 degrees at
        first then later by 15 degrees, the final position will be at 20 degrees and not 15 degrees with
        movement limitation of +/-170 degrees.

        Example: The function calls rotate the wrist 45 degrees counter-clockwise then an additional
        30 degrees in the same direction.
        >>> arm.rotate_wrist(45)
        >>> arm.rotate_wrist(30)
        """
        pass

    def move_arm(self, x: float, y: float, z: float) -> None:
        """It moves the Q-arm to target location based on a cartesian coordinate input, taking in three
        input arguments corresponding to x, y, and z coordinates in 3D space.

        Example: The Q-arm’s joints are rotated to move the arm to the specified xyz location where
        x = -0.6097, y = 0.2463, and z = 0.3643
        >>> arm.move_arm(-0.6097, 0.2463, 0.3643)
        """
        pass

    def home(self) -> None:
        """It moves the Q-arm to default position in the environment, corresponding to all joints being
        at 0 degrees and the gripper being fully open. When used, this function takes no arguments.

        Example: Calling the home function takes the arm back to the default position and returns
        zero for all joint angles and the gripper.
        >>> arm.home()
        0 0 0 0 0
        """

    def spawn_cage(self, value: int) -> int:
        """When this function is called, a container, based on the value passed, is spawned onto the
        ‘pick-up’ location. A valid value is a number between 1 and 6 (inclusive). 1,2,3 for small red,
        green and blue containers respectively, and 4,5,6 for large red, green and blue containers
        respectively.

        Example: This will spawn a small green container then a large blue container.
        >>> arm.spawn_cage(2)
        2
        >>> arm.spawn_cage(6)
        6
        """
        pass

    def open_red_autoclave(self, value: bool) -> None:
        """The function controls the opening and closing of the red autoclave corresponding to the input
        boolean. Passing True opens the drawer while passing False closes it.

        Example: The first line opens the red autoclave’s drawer and the second closes it.
        >>> arm.open_red_autoclave(True)
        >>> arm.open_red_autoclave(False)
        """
        pass

    def open_green_autoclave(self, value: bool) -> None:
        """The function controls the opening and closing of the green autoclave corresponding to the input
        boolean. Passing True opens the drawer while passing False closes it.

        Example: The first line opens the green autoclave’s drawer and the second closes it.
        >>> arm.open_green_autoclave(True)
        >>> arm.open_green_autoclave(False)
        """
        pass

    def open_blue_autoclave(self, value: bool) -> None:
        """The function controls the opening and closing of the blue autoclave corresponding to the input
        boolean. Passing True opens the drawer while passing False closes it.

        Example: The first line opens the blue autoclave’s drawer and the second closes it.
        >>> arm.open_blue_autoclave(True)
        >>> arm.open_blue_autoclave(False)
        """
        pass


    def control_gripper(self, value: float) -> None:
        """It controls the opening and closing of the gripper with degrees. A value of zero corresponding
        to fully open and 45 degrees correspond to fully closed. Function calls are relative, meaning
        when passing an angle greater than zero, the gripper will partially close but to fully open it
        again, you must pass the same number but with a negative sign in order to have a sum of
        zero. To partially open it, you can pass a smaller negative value.

        Example: The gripper is first fully closed and then fully opened. 
        >>> arm.conrol_gripper(45)
        >>> arm.conrol_gripper(-45)
        """
        pass

    def emg_left(self) -> float:
        """This function returns the value, between 0 and 1 (inclusive), of the EMG sensor
        corresponding to the position of the left arm.

        Example: The function call returns the reading of the left arm. A value of 1 indicates the arm
        is in full flexion.
        >>> arm.emg_left()
        1.0
        """
        pass

    def emg_right(self) -> float:
        """This function returns the value, between 0 and 1 (inclusive), of the EMG sensor
        corresponding to the position of the right arm.

        Example: The function call returns the reading of the right arm. A value of ~0.34 indicates
        the arm is slightly flexed.
        >>> arm.emg_right()
        0.34237128496170044
        """
        pass

    def effector_position(self) -> Tuple[float, float, float]:
        """It returns the xyz coordinates of the Q-arm’s location in 3D space at the time the function was
        called.

        Example: The function returns the cartesian location of the Q-arm in space as a 3-item list.
        >>> arm.effector_position()
        (0.4064, 0.0, 0.4826)
        """
        pass
