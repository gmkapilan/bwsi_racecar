"""
MIT BWSI Autonomous RACECAR
MIT License
racecar-neo-outreach-labs

File Name: grand_prix.py

Title: Grand Prix Day!

Author: Team 10

Purpose: Write a script to enable fully autonomous behavior from the RACECAR. The
RACECAR will traverse the obstacle course autonomously without human intervention.
Once the start button is pressed, the RACECAR must drive through the course until it
reaches the white cone at the end, in which it will then stop. You are disqualified if
you stop too far from the cone or hit the cone.

Note: There is no template code in this document to follow except for the RACECAR script
structure found in template.py. You are expected to use code written from previous labs
to complete this challenge. Good luck!

Expected Outcome: When the user runs the script, they must not be able to manually control
the RACECAR. The RACECAR must move forward on its own, traverse through the course, and then
stop on its own.
- The speed of the RACECAR can be controlled by a state machine or script, but not by the user
- The angle of the RACECAR should only be controlled by the center of the line contour
- The RACECAR sees the color RED as the highest priority, then GREEN, then BLUE
- The RACECAR must stop before the white cone at the end of the course. The RACECAR must stop
close enough to the cone such that it does not see the entirety of the white cone at the end
of the race. (less than 30 cm). The RACECAR must not hit the white cone.
"""

########################################################################################
# Imports
########################################################################################

import sys
import cv2 as cv

# If this file is nested inside a folder in the labs folder, the relative path should
# be [1, ../../library] instead.
sys.path.insert(1, '../../library')
import racecar_core
import racecar_utils as rc_utils

########################################################################################
# Global variables
########################################################################################

rc = racecar_core.create_racecar()

# Declare any global variables here

speed = 0 # Set speed of the RACECAR (-1 to 1)
angle = 0 # Set angle of the RACECAR (-1 to 1)

#fastSpeed = 1 # Speed for when fast is good
#normalSpeed = 0.4 # Speed for normal conditions
#rampSpeed = 0.3 # Speed for risky rampsfastSpeed = 1 # Speed for when fast is good
fastSpeed = 0.775 # Speed for when fast is good
normalSpeed = 0.4 # Speed for normal conditions
rampSpeed = 0.3 # Speed for risky ramps
speedStraightSpace = 75 # Distance from center that counts as a straight
speedTime = 0.2 # How long the RACECAR has to stay on a straight to speed up
timer = speedTime # DO NOT CHANGE
counter = 0

maxMidContour = None

contourCenter = None
contourArea = 0

MIN_CONTOUR_AREA = 100   # Minimum area needed to be valid contour
CROP_FLOOR = ((330, 0), (rc.camera.get_height(), rc.camera.get_width())) # Area of floor crop
CROP_MID = ((180, 0),(210, rc.camera.get_width())) # Area of midscreen crop

# Color thresholds
BLUE = ((104, 254, 254), (106, 255, 255))
GREEN = ((63,254,254),(65,255,255))
RED = ((0,254,254),(1,255,255))
#BLACK = ((, , ),(, , ))

# Color priority
COLOR_PRIORITY = (RED, BLUE, GREEN)

colors = {
    BLUE : "blue",
    GREEN : "green",
    RED : "red",
}

currentColor = None

########################################################################################
# Functions
########################################################################################

def rangeMap(value, oldLow, oldHigh, newLow, newHigh):
    return value / (oldHigh-oldLow) * (newHigh-newLow)

def updateContour():
    global contourCenter
    global contourArea
    global currentColor
    global maxMidContour

    # Extracts color camera frame
    image = rc.camera.get_color_image()

    if image is None:
        contourCenter = None
        contourArea = 0
    else:
        # Crops image to floor or midscreen only
        midImage = rc_utils.crop(image, CROP_MID[0], CROP_MID[1])
        image = rc_utils.crop(image, CROP_FLOOR[0], CROP_FLOOR[1])

        # Search for contours
        for color in COLOR_PRIORITY:
            contours = rc_utils.find_contours(image,color[0],color[1])
            if contours != ():
                currentColor = colors[color]
                break

        # Searches for contours in midscreen
        for color in COLOR_PRIORITY:
            midContours = rc_utils.find_contours(midImage,color[0],color[1])
            if midContours != ():
                break

        # Finds largest contour
        maxContour = rc_utils.get_largest_contour(contours, MIN_CONTOUR_AREA)
        maxMidContour = rc_utils.get_largest_contour(midContours, MIN_CONTOUR_AREA)

        if maxContour is not None:
            # Gets contour center
            contourCenter = rc_utils.get_contour_center(maxContour)

            # Gets contour area
            contourArea = rc_utils.get_contour_area(maxContour)

            # Draws largest contour in pink
            cv.drawContours(image, [maxContour], 0, (255, 0, 255), 3)

            # Draws contour center in yellow
            rc_utils.draw_circle(image,contourCenter)

        #hsvImage = cv.cvtColor(image, cv.COLOR_BGR2HSV)
        #print(hsvImage[149][320])

        # Displays floor/main image
        rc.display.show_color_image(image)

        # Displays midscreen image
        cv.namedWindow("Midscreen", cv.WINDOW_NORMAL)
        cv.imshow("Midscreen", midImage)

# [FUNCTION] The start function is run once every time the start button is pressed
def start():
    global speed
    global angle

    speed = 0
    angle = 0

    rc.drive.set_speed_angle(speed, angle)

# [FUNCTION] After start() is run, this function is run once every frame (ideally at
# 60 frames per second or slower depending on processing speed) until the back button
# is pressed
def update():
    global speed
    global angle
    global timer
    global counter

    updateContour()

    cameraWidth = rc.camera.get_width()

    # Max speed control
    # spc = speed control value
    spc=0
    if contourCenter is not None:
        if contourCenter[1] > cameraWidth // 2 - speedStraightSpace and contourCenter[1] < cameraWidth // 2 + speedStraightSpace:
            timer -= rc.get_delta_time()
            if timer <= 0:
                rc.drive.set_max_speed(fastSpeed)
                spc=5
            else:
                rc.drive.set_max_speed(normalSpeed)
                spc=4
        else:
            rc.drive.set_max_speed(normalSpeed)
            spc=4
            timer = speedTime
    else:
        rc.drive.set_max_speed(normalSpeed)
        spc=4
    # Ramp detector
    if maxMidContour is not None:
        rc.drive.set_max_speed(rampSpeed)
        spc=3
        counter = 35
    if counter > 0:
        rc.drive.set_max_speed(rampSpeed)
        spc = 3
        counter -= 1

    # Angle control based on contour center
    # Constants for PID control
    Kp = 0.6  # Proportional gain
    Ki = 0.2  # Integral gain
    Kd = 0.2  # Derivative gain
    prevError = 0
    integral = 0

    if contourCenter is not None:
        setpoint = cameraWidth // 2
        error = setpoint - contourCenter[1]
        error = rangeMap(error, -320, 320, -1, 1)

        # Proportional
        proportional = -1 * error

        # Integral
        integral += error * -1

        # Derivative
        derivative = error - prevError * -1

        angle = proportional * Kp + integral * Ki + derivative * Kd
        prevError = error

        angle = proportional

    print(f"speed control={spc} angle={angle}")


    # Speed control
    speed = 1

    # DRIVE
    rc.drive.set_speed_angle(speed, angle)

# [FUNCTION] update_slow() is similar to update() but is called once per second by
# default. It is especially useful for printing debug messages, since printing a
# message every frame in update is computationally expensive and creates clutter
def update_slow():
    pass # Remove 'pass and write your source code for the update_slow() function here

########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
