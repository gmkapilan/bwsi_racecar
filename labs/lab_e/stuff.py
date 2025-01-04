"""
MIT BWSI Autonomous RACECAR
MIT License
racecar-neo-outreach-labs

File Name: lab_e.py

Title: Lab E - Stoplight Challenge

Author: Cameron Tran

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
BLUE = ((90, 150, 50), (120, 255, 255))  # The HSV range for the color blue
GREEN = ((30,50,50),(80,255,255))  # The HSV range for the color green
RED = ((0,50,50),(10,255,255))  # The HSV range for the color red
ORANGE = ((10,50,50),(20,255,255)) # The HSV range for the color orange
YELLOW = ((22,50,50),(30,255,255)) # The HSV range for the color yellow
PURPLE = ((125,50,50),(165,255,255)) # The HSV range for the color purple
WHITE = ((0, 0, 250), (250, 5, 255))
colorThresholds = (BLUE, GREEN, ORANGE, RED, YELLOW, PURPLE, WHITE)
colors = ("blue","green","orange","red","yellow","purple","white")

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
    debugImage = rc.camera.get_color_image()

    if image is None:
        contour_center = None
        contour_area = 0
    else:
        # TODO Part 2: Search for line colors, and update the global variables
        # contour_center and contour_area with the largest contour found

        # Converts BGR image to HSV image
        hsv_image = cv.cvtColor(image, cv.COLOR_BGR2HSV)

        # Combines masks for all light colors
        mask = 0 # mask initialization
        for threshold in colorThresholds:
            mask += cv.inRange(hsv_image, threshold[0], threshold[1])

        # Finds contours in mask
        contours, _ = cv.findContours(mask, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)

        # If contours were found:
        if len(contours) > 0:
            # Finds largest contour
            max_contour = contours[0]
            CONTOUR_MIN = 30
            for contour in contours:
                if cv.contourArea(contour) > CONTOUR_MIN:
                    if cv.contourArea(contour) > cv.contourArea(max_contour):
                        max_contour = contour

            # If there is a big enough contour
            if len(max_contour) > 0:
                # Assigns area and center of largest contour
                contour_area = cv.contourArea(max_contour)
                contour_center = rc_utils.get_contour_center(max_contour)
                if contour_center != None:
                    
                    # Draws largest contour and its center
                    cv.drawContours(debugImage, [max_contour], 0, (255, 0, 255), 3)
                    cv.circle(debugImage, (contour_center[1], contour_center[0]), 3, (255, 0, 255), -1)

                # TODO Part 3: Repeat the search for all potential traffic light colors,
                # then select the correct color of traffic light detected.

                    # Takes contour center color
                    blue = image[contour_center[0]][contour_center[1]][0]
                    green = image[contour_center[0]][contour_center[1]][1]
                    red = image[contour_center[0]][contour_center[1]][2]
                    BGR_color = (blue, green, red)
                else:
                    # Set color to black if no big contours
                    BGR_color = (0, 0, 0)
        else:
            # Set color to black if no contours
            BGR_color = (0, 0, 0)

        # Fills image with contour center color
        BGR_image = np.zeros((300, 300, 3), np.uint8)
        BGR_image[:] = BGR_color

        if len(queue) == 0:
            # Converts BGR to HSV
            center_HSV_image = cv.cvtColor(BGR_image, cv.COLOR_BGR2HSV)

            counter = 0
            for threshold in colorThresholds:
                global stoplight_color
                counter += 1
                if (center_HSV_image[0][0] >= threshold[0]).all() and (center_HSV_image[0][0] <= threshold[1]).all():
                    stoplight_color = colors[counter-1]

        # Display the all images to the screen windows
        # Main color camera
        rc.display.show_color_image(image)
        # Debug color camera
        cv.namedWindow("Debug Image", cv.WINDOW_NORMAL)
        cv.imshow("Debug Image", debugImage)
        # Mask display
        cv.namedWindow("Mask Display", cv.WINDOW_NORMAL)
        cv.imshow("Mask Display", mask)
        # Contour center color
        cv.namedWindow("Contour Center Color", cv.WINDOW_NORMAL)
        cv.imshow("Contour Center Color", BGR_image)

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
    global stoplight_color
    speed = 0
    angle = 0

    update_contour()

    # TODO Part 2: Complete the conditional tree with the given constraints.
    if stoplight_color == "blue":
        # Call the correct function to append the instructions to the list
        print("Blue: Right turn")
        stoplight_color = ""
        queue.append([2,1,0])
        queue.append([1.32,1,1])
        queue.append([0.2,1,0])
    elif stoplight_color == "orange":
        # Call the correct function to append the instructions to the list
        print("Orange: Left turn")
        stoplight_color = ""
        queue.append([2,1,0])
        queue.append([1.2,1,-1])
        queue.append([0.2,1,0])
    elif stoplight_color == "green":
        print("Green: Straight ahead")
        stoplight_color = ""
        queue.append([3,1,0])
    elif stoplight_color != "":
        print("STOP")
        stoplight_color = ""
    
    # ... You may need more elif/else statements

    # TODO Part 3: Implement a way to execute instructions from the queue once they have been placed
    # by the traffic light detector logic (Hint: Lab 2)
    if len(queue) > 0:
        speed = queue[0][1]
        angle = queue[0][2]
        queue[0][0] -= rc.get_delta_time()
        if queue[0][0] <= 0:
            queue.pop(0)
    else:
        speed = 0
        angle = 0

    # Send speed and angle commands to the RACECAR
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

# [FUNCTION] Appends the correct instructions to make a 90 degree left turn to the queue
def turnLeft():
    global queue

    # TODO Part 5: Complete the rest of this function with the instructions to make a left turn

# [FUNCTION] Appends the correct instructions to go straight through the intersectionto the queue
def goStraight():
    global queue

    # TODO Part 6: Complete the rest of this function with the instructions to make a left turn

# [FUNCTION] Clears the queue to stop all actions
def stopNow():
    global queue
    queue.clear()

def update_slow():
    pass
########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
