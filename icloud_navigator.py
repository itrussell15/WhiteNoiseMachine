# -*- coding: utf-8 -*-
"""
Created on Sat May 15 13:26:53 2021

@author: Schmuck
"""

from utils import iCloud, Sonos, time_check
import datetime, time

cloud = iCloud()
player = Sonos()
format_time = lambda x: x.strftime("%H:%M:%S %m-%d-%Y")

def create_file():
    with open("log.txt", "w") as f:
        f.write("Beginning of the log at {}".format(datetime.datetime.now()))
        f.close()

def write_to_log(message, to_print = False):
    if to_print:
        print(message)
    with open("log.txt", "a") as f:
        f.write("\n{date} --> {message}".format(date = datetime.datetime.now(), message = message))
        f.close()
        
create_file()
print("Starting Program")

old = None

while True:
    
    if time_check(hour = 23, minute = 15):
        player.check_is_playing()
        if not player.is_playing:
            write_to_log("Not Playing Check Passed")
            
            if cloud.is_home():
                write_to_log("Is Home Check Passed")
                
                if cloud.is_charging():
                    write_to_log("All tests passed! Music Started Playing!", to_print = True)
                    player.play_fresh()
        else:
            current = player.current_track()
        if current != old:
            if current == "":
                player.set_volume(0)
                write_to_log("Ad detected, volume turned down", to_print = True)
            else:
                write_to_log("Now Playing {}".format(current), to_print = True)
                if player.volume != player.desired_volume:
                    write_to_log("Ad done playing, turned volume back to desired", to_print = True)
                    player.ramp_volume()
            old = current

time.sleep(10)
                    
#    if time_check(hour = 6, minute = 30):
#        write_to_log("Morning Time Check Passed")
#        if player.is_playing:
#            write_to_log("Playing Check Passed")
#            player.stop()
#            write_to_log("Muisic Stopped!")
        