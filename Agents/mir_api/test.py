#!/usr/bin/env python2 
# coding: utf8
"""
authors: Fabrice DUVAL and Ayman DAMOUN  
2021
"""
from mir_utils import mymir
import requests
MirIp = '10.191.76.55'

mir_arm = mymir(MirIp)

#test = mir_arm.move_to_position(x=0.11445918679237366,y=0.12835092842578888,yaw=1.4513847827911377)
#test = mir_arm.move_to_position(x=1.0049165487289429, y=0.2397424578666687, yaw=2.5829944610595703)
#print(mir_arm.getposition())
#test = mir_arm.add_to_mission_queue(mission ='e406025a-6b7d-11eb-ae10-f44d306ef93b')   # go pt 1 devant porte VR
mir_arm.clear_mission_queue()