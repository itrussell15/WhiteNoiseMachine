# -*- coding: utf-8 -*-
"""
Created on Sat May 15 13:26:53 2021

@author: Schmuck
"""

from utils import iCloud, Sonos, Logging, time_check
import datetime, time

cloud = iCloud()
player = Sonos()
log = Logging()
format_time = lambda x: x.strftime("%H:%M:%S %m-%d-%Y")

# def create_file():
#     with open("log.txt", "w") as f:
#         f.write("Beginning of the log at {}".format(datetime.datetime.now()))
#         f.close()

# def write_to_log(message, to_print = False):
#     if to_print:
#         print(message)
#     with open("log.txt", "a") as f:
#         f.write("\n{date} --> {message}".format(date = datetime.datetime.now(), message = message))
#         f.close()
        
# create_file()
log.write_to_log("Program Starting", action = "GENERIC", to_print = True)

old = None

while True:
    
    if time_check(hour = 23, minute = 15):
        player.check_is_playing()
        
        if not player.is_playing:
            log.write_to_log("Not Playing Check Passed", action = "CHECK")
            cloud.update_phone()
            
            if cloud.is_home():
                log.write_to_log("Is Home Check Passed", "CHECK")
                
                if cloud.is_charging():
                    log.write_to_log("All tests passed! Music Started Playing!", to_print = True, action = "CHECK")
                    player.play_fresh()
        else:
            current = player.current_track()
            if current != old:
                if current == "":
                    log.write_to_log("Ad detected, volume turned down", to_print = True, action = "MUSIC")
                else:
                    log.write_to_log("Now Playing {}".format(current), to_print = True, action = "MUSIC")
                    if player.volume != player.desired_volume:
                        log.write_to_log("Ad done playing, turned volume back to desired", to_print = True, action = "MUSIC")
                        player.ramp_volume()
                old = current

time.sleep(30)        