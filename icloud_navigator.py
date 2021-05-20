# -*- coding: utf-8 -*-
"""
Created on Sat May 15 13:26:53 2021

@author: Schmuck
"""

from utils import iCloud, Sonos, time_check
import datetime

cloud = iCloud()
player = Sonos()

format_time = lambda x: x.strftime("%H:%M:%S %m-%d-%Y")

def create_file():
    with open("log.txt", "w") as f:
        f.write("Beginning of the log at {}".format(datetime.datetime.now()))
        f.close()

def write_to_log(message):
    with open("log.txt", "a") as f:
        f.write("\n{date} --> {message}".format(date = datetime.datetime.now(), message = message))
        f.close()
        
create_file()

while True:
    
    if time_check(hour = 23, minute = 15):
        write_to_log("Night Time Check Passed")
        if not player.is_playing:
            write_to_log("Not Playing Check Passed")
            if cloud.is_home():
                write_to_log("Is Home Check Passed")
                if cloud.is_charging():
                    write_to_log("All tests passed! Music Started Playing!")
                    player.play_fresh()
    
    if time_check(hour = 6, minute = 30):
        write_to_log("Morning Time Check Passed")
        if player.is_playing:
            write_to_log("Playing Check Passed")
            player.stop()
            write_to_log("Muisic Stopped!")
        