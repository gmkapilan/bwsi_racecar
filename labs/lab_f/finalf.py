"""
MIT BWSI Autonomous RACECAR
MIT License
racecar-neo-outreach-labs

File Name: lab_f.py

Title: Lab F - Line Follower

Author: [PLACEHOLDER] << [Write your name or team name here]

Purpose: Write a script to enable fully autonomous behavior from the RACECAR. The
RACECAR should automatically identify the color of a line it sees, then drive on the
center of the line throughout the obstacle course. The RACECAR should also identify
color changes, following colors with higher priority than others. Complete the lines 
of code under the #TODO indicators to complete the lab.

Expected Outcome: When the user runs the script, they are able to control the RACECAR
using the following keys:
- When the right trigger is pressed, the RACECAR moves forward at full speed
- When the left trigger is pressed, the RACECAR, moves backwards at full speed
- The angle of the RACECAR should only be controlled by the center of the line contour
- The RACECAR sees the color RED as the highest priority, then GREEN, then BLUE
"""

########################################################################################
# Imports
########################################################################################

import sys
import cv2 as cv
import numpy as np

# If this file is nested inside a folder in the labs folder, the relative path should
# be [1, ../../library] instead.
sys.path.insert(1, "../../library")
import racecar_core
import racecar_utils as rc_utils

########################################################################################
# Global variables
########################################################################################
color_priority = 0
rc = racecar_core.create_racecar()

# >> Constants
# The smallest contour we will recognize as a valid contour
MIN_CONTOUR_AREA = 30

# A crop window for the floor directly in front of the car
CROP_FLOOR = ((360, 0), (rc.camera.get_height(), rc.camera.get_width()))

# TODO Part 1: Determine the HSV color threshold pairs for GREEN and RED
# Colors, stored as a pair (hsv_min, hsv_max) Hint: Lab E!
BLUE = ((90, 50, 50), (120, 255, 255))  # The HSV range for the color blue
GREEN = ((30, 50, 50), (80, 255, 255))  # The HSV range for the color green
RED = ((0, 50, 50), (10, 255, 255))  # The HSV range for the color red

#Color priority: Red >> Green >> Blue
CPL = [(1, 2, 0), (1, 0, 2), (0, 2, 1), (0, 1, 2), (2, 1, 0), (2, 0, 1)]
# >> Variables
speed = 0.0  # The current speed of the car
angle = 0.0  # The current angle of the car's wheels
contour_center = None  # The (pixel row, pixel column) of contour
contour_area = 0  # The area of contour


MAGENTA = ((145, 50, 50), (170, 255, 255))
BLACK = ((0, 0, 0), (180, 255, 50))
WHITE = ((0, 0, 200), (180, 50, 255))
ORANGE = ((10, 50, 50), (20, 255, 255))
YELLOW = ((20, 50, 50), (30, 255, 255))
PURPLE = ((125, 50, 50), (155, 255, 255))
#Color Cone List
CCL = [((0, 0, 0), (179, 255, 55)), ((138, 200, 150), (145, 220, 225)), ((125, 50, 50), (155, 255, 255)), ((10, 50, 50), (20, 255, 255)), ((102, 50, 150), (110, 70, 210)), ((25, 50, 50), (38, 255, 255))]
########################################################################################
# Functions
########################################################################################

# [FUNCTION] Finds contours in the current color image and uses them to update 
# contour_center and contour_area
def update_contour():
    global contour_center
    global contour_area
    global color_priority
    global speed

    image = rc.camera.get_color_image()

    if image is None:
        contour_center = None
        contour_area = 0
    else:
        # Crop the image to the floor directly in front of the car
        image = rc_utils.crop(image, CROP_FLOOR[0], CROP_FLOOR[1])

        # TODO Part 2: Search for line colors, and update the global variables
        # contour_center and contour_area with the largest contour found
        contour_blue = rc_utils.find_contours(image, BLUE[0], BLUE[1])
        contour_green = rc_utils.find_contours(image, GREEN[0], GREEN[1])
        contour_red = rc_utils.find_contours(image, RED[0], RED[1])

        #Finds largest contour
        contour_color_list = []
        contour_color_list.append(rc_utils.get_largest_contour(contour_blue, MIN_CONTOUR_AREA))
        contour_color_list.append(rc_utils.get_largest_contour(contour_green, MIN_CONTOUR_AREA))
        contour_color_list.append(rc_utils.get_largest_contour(contour_red, MIN_CONTOUR_AREA))

        #Lowest contour priority
        if contour_color_list[CPL[color_priority][2]] is not None:
            contour_center = rc_utils.get_contour_center(contour_color_list[CPL[color_priority][2]])
            contour_area = rc_utils.get_contour_area(contour_color_list[CPL[color_priority][2]])

            rc_utils.draw_contour(image, contour_color_list[CPL[color_priority][2]])
            rc_utils.draw_circle(image, contour_center)
        
        #Middle contour priority
        if contour_color_list[CPL[color_priority][1]] is not None:
            contour_center = rc_utils.get_contour_center(contour_color_list[CPL[color_priority][1]])
            contour_area = rc_utils.get_contour_area(contour_color_list[CPL[color_priority][1]])

            rc_utils.draw_contour(image, contour_color_list[CPL[color_priority][1]])
            rc_utils.draw_circle(image, contour_center)
        
        #Highest contour priority
        if contour_color_list[CPL[color_priority][0]] is not None:
            contour_center = rc_utils.get_contour_center(contour_color_list[CPL[color_priority][0]])
            contour_area = rc_utils.get_contour_area(contour_color_list[CPL[color_priority][0]])

            rc_utils.draw_contour(image, contour_color_list[CPL[color_priority][0]])
            rc_utils.draw_circle(image, contour_center)
        
        if rc.controller.was_pressed(rc.controller.Button.A):
            color_priority += 1
        if color_priority > 5:
            color_priority = 0
        print(f"{color_priority} is selected")

    #Cone colors and contours
    MIN_CONE_AREA = 30
    image2 = rc.camera.get_color_image()
    conecolors = 0
    coneContours = ()
    coneContours += rc_utils.find_contours(image2, CCL[color_priority][0], CCL[color_priority][1])
    maxconecontour = rc_utils.get_largest_contour(coneContours, MIN_CONE_AREA)

    if maxconecontour is not None:
        cone_area = rc_utils.get_contour_area(maxconecontour)
        rc_utils.draw_contour(image2, maxconecontour)
    else:
        cone_area = 0
    
    if cone_area > 21000:
        speed = 0
    # Display the image to the screen
    rc.display.show_color_image(image)



# [FUNCTION] The start function is run once every time the start button is pressed
def start():
    global speed
    global angle

    # Initialize variables
    speed = 0
    angle = 0

    # Set initial driving speed and angle
    rc.drive.set_speed_angle(speed, angle)

    # Set update_slow to refresh every half second
    rc.set_update_slow_time(0.5)

    # Print start message
    print(
        ">> Lab 2A - Color Image Line Following\n"
        "\n"
        "Controls:\n"
        "   Right trigger = accelerate forward\n"
        "   Left trigger = accelerate backward\n"
        "   A button = print current speed and angle\n"
        "   B button = print contour center and area"
    )

# [FUNCTION] After start() is run, this function is run once every frame (ideally at
# 60 frames per second or slower depending on processing speed) until the back button
# is pressed  
def update():
    """
    After start() is run, this function is run every frame until the back button
    is pressed
    """
    global speed
    global angle

    # Search for contours in the current color image
    update_contour()

    # TODO Part 3: Determine the angle that the RACECAR should receive based on the current 
    # position of the center of line contour on the screen. Hint: The RACECAR should drive in
    # a direction that moves the line back to the center of the screen.
    
    #Proportional control algorithm
    if contour_center is not None:
        setpoint = rc.camera.get_width() // 2
        error = setpoint - contour_center[1]
        angle = rc_utils.remap_range(contour_center[1], 0, rc.camera.get_width(), -1, 1)

    # Use the triggers to control the car's speed
    rt = rc.controller.get_trigger(rc.controller.Trigger.RIGHT)
    lt = rc.controller.get_trigger(rc.controller.Trigger.LEFT)

    if rc.controller.was_pressed(rc.controller.Button.B):
        speed = 0.4
    rc.drive.set_speed_angle(speed, angle)

    if rc.controller.was_pressed(rc.controller.Button.X):
        speed = 0

    # Print the current speed and angle when the A button is held down
    if rc.controller.is_down(rc.controller.Button.A):
        print("Speed:", speed, "Angle:", angle)

    # Print the center and area of the largest contour when B is held down
    if rc.controller.is_down(rc.controller.Button.B):
        if contour_center is None:
            print("No contour found")
        else:
            print("Center:", contour_center, "Area:", contour_area)

# [FUNCTION] update_slow() is similar to update() but is called once per second by
# default. It is especially useful for printing debug messages, since printing a 
# message every frame in update is computationally expensive and creates clutter
def update_slow():
    """
    After start() is run, this function is run at a constant rate that is slower
    than update().  By default, update_slow() is run once per second
    """
    # Print a line of ascii text denoting the contour area and x-position
    if rc.camera.get_color_image() is None:
        # If no image is found, print all X's and don't display an image
        print("X" * 10 + " (No image) " + "X" * 10)
    else:
        # If an image is found but no contour is found, print all dashes
        if contour_center is None:
            print("-" * 32 + " : area = " + str(contour_area))

        # Otherwise, print a line of dashes with a | indicating the contour x-position
        else:
            s = ["-"] * 32
            s[int(contour_center[1] / 20)] = "|"
            print("".join(s) + " : area = " + str(contour_area))


########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
