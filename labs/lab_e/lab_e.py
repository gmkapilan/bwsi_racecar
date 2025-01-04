"""
MIT BWSI Autonomous RACECAR
MIT License
racecar-neo-outreach-labs

File Name: lab_e.py

Title: Lab E - Stoplight Challenge

Author: Kapilan Karunakaran

Purpose: Write a script to enable autonomous behavior from the RACECAR. When
the RACECAR sees a stoplight object (colored cube in the simulator), respond accordingly
by going straight, turning right, turning left, or stopping. Append instructions to the
queue depending on whether the position of the RACECAR relative to the stoplight reaches
a certain threshold, and be able to respond to traffic lights at consecutive intersections. 

Expected Outcome: When the user runs the script, the RACECAR should control itself using
the following constraints:
- When the RACECAR sees a BLUE traffic light, make a right turn at the intersection
- When the RACECAR sees an ORANGE traffic light, make a left turn at the intersection
- When the RACECAR sees a GREEN traffic light, go straight
- When the RACECAR sees a RED traffic light, stop moving,
- When the RACECAR sees any other traffic light colors, stop moving.

Considerations: Since the user is not controlling the RACECAR, be sure to consider the
following scenarios:
- What should the RACECAR do if it sees two traffic lights, one at the current intersection
and the other at the intersection behind it?
- What should be the constraint for adding the instructions to the queue? Traffic light position,
traffic light area, or both?
- How often should the instruction-adding function calls be? Once, twice, or 60 times a second?

Environment: Test your code using the level "Neo Labs > Lab 3: Stoplight Challenge".
By default, the traffic lights should direct you in a counterclockwise circle around the course.
For testing purposes, you may change the color of the traffic light by first left-clicking to 
select and then right clicking on the light to scroll through available colors.
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

rc = racecar_core.create_racecar()

# >> Constants
# The smallest contour we will recognize as a valid contour (Adjust threshold!)
MIN_CONTOUR_AREA = 30

# TODO Part 1: Determine the HSV color threshold pairs for ORANGE, GREEN, RED, YELLOW, and PURPLE
# Colors, stored as a pair (hsv_min, hsv_max)
BLUE = ((90, 50, 50), (120, 255, 255))  # The HSV range for the color blue
GREEN = ((35, 50, 50), (75, 255, 255))  # The HSV range for the color green
RED = ((170, 50, 50), (5, 255, 255))  # The HSV range for the color red
ORANGE = ((10, 50, 50), (20, 255, 255)) # The HSV range for the color orange
YELLOW = ((20, 50, 50), (30, 255, 255)) # The HSV range for the color yellow
PURPLE = ((130, 50, 50), (160, 255, 255)) # The HSV range for the color purple

# >> Variables
contour_center = None  # The (pixel row, pixel column) of contour
contour_area = 0  # The area of contour

queue = [] # The queue of instructions
stoplight_color = "" # The current color of the stoplight

########################################################################################
# Functions
########################################################################################

# [FUNCTION] Finds contours in the current color image and uses them to update 
# contour_center and contour_area
def update_contour():
    global contour_center
    global contour_area

    image = rc.camera.get_color_image()
    image = rc_utils.crop(image, (50, 0), (rc.camera.get_height(), rc.camera.get_width()))
                          
    hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)

    maskBlue = cv.inRange(hsv, BLUE[0], BLUE[1])
    maskGreen = cv.inRange(hsv, GREEN[0], GREEN[1])
    maskRed = cv.inRange(hsv, RED[0], RED[1])
    maskYellow = cv.inRange(hsv, YELLOW[0], YELLOW[1])
    maskPurple = cv.inRange(hsv, PURPLE[0], PURPLE[1])

    contourBlue, _ = cv.findContours(maskBlue, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
    contourRed, _ = cv.findContours(maskRed, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
    contourGreen, _ = cv.findContours(maskGreen, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
    contourYellow, _ = cv.findContours(maskYellow, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
    contourPurple, _ = cv.findContours(maskPurple, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)

    rc.display.show_color_image(maskBlue)

    if image is None:
        contour_center = None
        contour_area = 0
    else:
        # TODO Part 2: Search for line colors, and update the global variables
        # contour_center and contour_area with the largest contour found
        contours = rc_utils.find_contours(image, BLUE[0], BLUE[1])
        contour = rc_utils.get_largest_contour(contours, MIN_CONTOUR_AREA)

        if contour is not None:
            contour_center = rc_utils.get_contour_center(contour)
            contour_area = rc_utils.get_contour_area(contour)
        else:
            contour_center = None
            contour_area = 0
        # TODO Part 3: Repeat the search for all potential traffic light colors,
        # then select the correct color of traffic light detected.

        #RED
        contours = rc_utils.find_contours(image, RED[0], RED[1])
        contour = rc_utils.get_largest_contour(contours, MIN_CONTOUR_AREA)

        if contour is not None:
            contour_center = rc_utils.get_contour_center(contour)
            contour_area = rc_utils.get_contour_area(contour)
        else:
            contour_center = None
            contour_area = 0

        #GREEN
        contours = rc_utils.find_contours(image, GREEN[0], GREEN[1])
        contour = rc_utils.get_largest_contour(contours, MIN_CONTOUR_AREA)

        if contour is not None:
            contour_center = rc_utils.get_contour_center(contour)
            contour_area = rc_utils.get_contour_area(contour)
        else:
            contour_center = None
            contour_area = 0
        
        #ORANGE
        contours = rc_utils.find_contours(image, ORANGE[0], ORANGE[1])
        contour = rc_utils.get_largest_contour(contours, MIN_CONTOUR_AREA)

        if contour is not None:
            contour_center = rc_utils.get_contour_center(contour)
            contour_area = rc_utils.get_contour_area(contour)
        else:
            contour_center = None
            contour_area = 0

        #YELLOW
        contours = rc_utils.find_contours(image, YELLOW[0], YELLOW[1])
        contour = rc_utils.get_largest_contour(contours, MIN_CONTOUR_AREA)

        if contour is not None:
            contour_center = rc_utils.get_contour_center(contour)
            contour_area = rc_utils.get_contour_area(contour)
        else:
            contour_center = None
            contour_area = 0
        
        #PURPLE
        contours = rc_utils.find_contours(image, PURPLE[0], PURPLE[1])
        contour = rc_utils.get_largest_contour(contours, MIN_CONTOUR_AREA)

        if contour is not None:
            contour_center = rc_utils.get_contour_center(contour)
            contour_area = rc_utils.get_contour_area(contour)
        else:
            contour_center = None
            contour_area = 0
        
        #need to find a way to make the racecar recognize the contour and its color

        # Display the image to the screen
    #rc.display.show_color_image(image)

# [FUNCTION] The start function is run once every time the start button is pressed
def start():

    # Set initial driving speed and angle
    rc.drive.set_speed_angle(0,0)

    # Set update_slow to refresh every half second
    rc.set_update_slow_time(0.5)

    # Print start message (You may edit this to be more informative!)
    print(
        ">> Lab 3 - Stoplight Challenge\n"
        "\n"
        "Controls:\n"
        "   A button = print current speed and angle\n"
        "   B button = print contour center and area"
    )

# [FUNCTION] After start() is run, this function is run once every frame (ideally at
# 60 frames per second or slower depending on processing speed) until the back button
# is pressed  
def update():
    global queue

    update_contour()

    # TODO Part 2: Complete the conditional tree with the given constraints.
    # Moved all this information to Part 3

    # TODO Part 3: Implement a way to execute instructions from the queue once they have been placed
    # by the traffic light detector logic (Hint: Lab 2)

    if len(queue) > 0:
        time, speed, angle = queue[0]
        time -= rc.get_delta_time()
        if time <= 0:
            queue.pop(0)
        else:
            queue[0] = (time, speed, angle)
    elif len(queue) == 0:
        if stoplight_color == "BLUE":
            turnRight()
        elif stoplight_color == "ORANGE":
            turnLeft()
        elif stoplight_color == "GREEN":
            goStraight()
        elif stoplight_color == "RED":
            stopNow()
        else:
            stopNow()

    # Send speed and angle commands to the RACECAR
    speed = 0.5
    angle = 0
    rc.drive.set_speed_angle(speed, angle)

    # Print the current speed and angle when the A button is held down
    if rc.controller.is_down(rc.controller.Button.A):
        print("Speed:", speed, "Angle:", angle)

    # Print the center and area of the largest contour when B is held down
    if rc.controller.is_down(rc.controller.Button.B):
        if contour_center is None:
            print("No contour found")
        else:
            print("Center:", contour_center, "Area:", contour_area)

# [FUNCTION] Appends the correct instructions to make a 90 degree right turn to the queue
def turnRight():
    global queue

    # TODO Part 4: Complete the rest of this function with the instructions to make a right turn
    print("Blue light detected, turning right.")
    queue.append([1, 0.5, 1])

# [FUNCTION] Appends the correct instructions to make a 90 degree left turn to the queue
def turnLeft():
    global queue

    # TODO Part 5: Complete the rest of this function with the instructions to make a left turn
    print("Orange light detected, turning left.")
    queue.append([1, 0.5, -1])

# [FUNCTION] Appends the correct instructions to go straight through the intersection to the queue
def goStraight():
    global queue

    # TODO Part 6: Complete the rest of this function with the instructions to go straight
    print("Green light detected, continuing straight.")
    queue.append([3, 1, 0])

# [FUNCTION] Clears the queue to stop all actions
def stopNow():
    global queue
    queue.clear()
    print("Red light detected, stopping.")
    queue.append([5, 0, 0])

########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update_contour, update)
    rc.go()