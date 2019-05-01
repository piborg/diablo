#!/usr/bin/env python

###
#
# diabloJoystick.py: A script for controlling motors with the Diablo using a joystick.
#
# 2019-04-26
#
###

# Load library functions we want
from __future__ import print_function
from diablo import *
from time import sleep
from os import environ
from sys import exit, stdout, stderr
import pygame

# Re-direct our output to standard error, we need to ignore standard out to hide some nasty print statements from pygame
stdout = stderr

# Set up the Diablo
DIABLO = Diablo()
#DIABLO.i2cAddress = 0x44                  # Uncomment and change the value if you have changed the board address
DIABLO.Init()
if not DIABLO.foundChip:
    boards = ScanForDiablo()
    if len(boards) == 0:
        print('No Diablo found, check you are attached :)')
    else:
        print('No Diablo at address %02X, but we did find boards:' % (DIABLO.i2cAddress))
        for board in boards:
            print('    %02X (%d)' % (board, board))
        print('If you need to change the I2C address change the set-up line so it is correct, e.g.')
        print('DIABLO.i2cAddress = 0x%02X' % (boards[0]))
    exit()
#DIABLO.SetEpoIgnore(True)                 # Uncomment to disable EPO latch, needed if you do not have a switch / jumper
DIABLO.ResetEpo()

# Settings for the joystick
axisUpDown = 1                     	    # Joystick axis to read for up / down position
axisUpDownInverted = False              # Set this to True if up and down appear to be swapped
axisLeftRight = 2                       # Joystick axis to read for left / right position
axisLeftRightInverted = False           # Set this to True if left and right appear to be swapped
buttonResetEpo = 3                      # Joystick button number to perform an EPO reset (Start)
buttonFast = 8                          # Joystick button number for driving fast whilst held (L2)
slowFactor = 0.5                        # Speed to slow to when the drive fast button is not held, e.g. 0.5 would be half speed
buttonFastTurn = 9                      # Joystick button number for turning fast (R2)
interval = 0.00                         # Time between updates in seconds, smaller responds faster but uses more processor time

# Set up pygame
environ["SDL_VIDEODRIVER"] = "dummy" # Removes the need to have a GUI window
pygame.init()
pygame.joystick.init()
pygame.display.set_mode((1,1))
joystick = pygame.joystick.Joystick(0)
joystick.init()

try:
    print('Motors are ready to drive.')
    print('Press CTRL+C to quit')
    driveLeft = 0.0
    driveRight = 0.0
    running = True
    hadEvent = False
    upDown = 0.0
    leftRight = 0.0
    # Loop indefinitely
    while running:
        # Get the latest events from the system
        hadEvent = False
        events = pygame.event.get()
        # Handle each event individually
        for event in events:
            if event.type == pygame.QUIT:
                # User exit
                running = False
            elif event.type == pygame.JOYBUTTONDOWN:
                # A button on the joystick just got pushed down
                hadEvent = True
            elif event.type == pygame.JOYAXISMOTION:
                # A joystick has been moved
                hadEvent = True
            if hadEvent:
                # Read axis positions (-1 to +1)
                if axisUpDownInverted:
                    upDown = -joystick.get_axis(axisUpDown)
                else:
                    upDown = joystick.get_axis(axisUpDown)
                if axisLeftRightInverted:
                    leftRight = -joystick.get_axis(axisLeftRight)
                else:
                    leftRight = joystick.get_axis(axisLeftRight)
                # Apply steering speeds
                if not joystick.get_button(buttonFastTurn):
                    leftRight *= 0.5
                # Determine the drive power levels
                driveLeft = -upDown
                driveRight = -upDown
                if leftRight < -0.05:
                    # Turning left
                    driveLeft *= 1.0 + (2.0 * leftRight)
                elif leftRight > 0.05:
                    # Turning right
                    driveRight *= 1.0 - (2.0 * leftRight)
                # Check for button presses
                if joystick.get_button(buttonResetEpo):
                    DIABLO.ResetEpo()
                if not joystick.get_button(buttonFast):
                    driveLeft *= slowFactor
                    driveRight *= slowFactor
                # Set the motors to the new speeds
                DIABLO.SetMotor1(driveLeft)
                DIABLO.SetMotor2(driveRight)
        # Wait for the interval period
        sleep(interval)
    # Disable all drives
    DIABLO.MotorsOff()
except KeyboardInterrupt:
    # CTRL+C exit, disable all drives
    DIABLO.MotorsOff()
    print('Terminated')
print()
