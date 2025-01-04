"""
MIT BWSI Autonomous RACECAR
MIT License
bwsix RC101 - Fall 2023

File Name: template.py << [Modify with your own file name!]

Title: Controller Testing << [Modify with your own title]

Author: Kapilan Karunakaran << [Write your name or team name here]

Purpose: TO verify functions from the controller library and to observe the output of these functions << [Write the purpose of the script here]

Expected Outcome: Test  button, trigger, and joystick commands to verify their output << [Write what you expect will happen when you run
the script.]
"""

########################################################################################
# Imports
########################################################################################

import sys

# If this file is nested inside a folder in the labs folder, the relative path should
# be [1, ../../library] instead.
sys.path.insert(1, '../../library')
import racecar_core

########################################################################################
# Global variables
########################################################################################

rc = racecar_core.create_racecar()

# Declare any global variables here
global counter
counter = 0

########################################################################################
# Functions
########################################################################################

# [FUNCTION] The start function is run once every time the start button is pressed
def start():
    pass # Remove 'pass' and write your source code for the start() function here

# [FUNCTION] After start() is run, this function is run once every frame (ideally at
# 60 frames per second or slower depending on processing speed) until the back button
# is pressed  
def update():  # Remove 'pass' and write your source code for the update() function here
    if rc.controller.was_pressed(rc.controller.Button.A):
        print(f"Hello World!")

    if rc.controller.was_pressed(rc.controller.Button.B):
        print(f"Welcome to RACECAR Kapilan!")

    if rc.controller.is_down(rc.controller.Button.X):
        global counter
        counter += rc.get_delta_time()
        print(f"{round(counter,2)} seconds have passed since the program started!")
            
    if rc.controller.was_released(rc.controller.Button.Y): 
        print(f"{round(counter,2)} seconds have passed since the program started!")

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
