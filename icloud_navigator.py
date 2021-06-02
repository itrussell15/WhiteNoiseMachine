# -*- coding: utf-8 -*-
"""
Created on Sat May 15 13:26:53 2021

@author: Schmuck
"""

from utils import iCloud, Sonos, Logging, time_check
import time

cloud = iCloud()
player = Sonos()
log = Logging()


log.write_to_log("Program Starting", action = "GENERIC", to_print = True)

old = None

while True:
    
    player.check_is_playing()
    if not player.is_playing and time_check(hour = 23, minute = 15):
        log.write_to_log("Not Playing Check Passed", action = "CHECK")
        cloud.update_phone()
            
        if cloud.is_home():
            log.write_to_log("Is Home Check Passed", "CHECK")
            
            player.check_is_playing()
            if cloud.is_charging() and player.is_playing:
                log.write_to_log("All tests passed! Music Started Playing!", to_print = True, action = "CHECK")
                player.play_fresh()
    else:
        if player.is_playing:
            current = player.current_track()
            if current != old:
                if current == "":
                    log.write_to_log("Ad detected, volume turned down", to_print = True, action = "MUSIC")
                    player.set_volume(0)
                else:
                    log.write_to_log("Now Playing {}".format(current), to_print = True, action = "MUSIC")
                    if player.volume != player.desired_volume:
                        log.write_to_log("Ad done playing, turned volume back to desired", to_print = True, action = "MUSIC")
                        player.ramp_volume()
                old = current

time.sleep(10)        