# -*- coding: utf-8 -*-
"""
Created on Sat May 15 13:26:53 2021

@author: Schmuck
"""

from utils import iCloud, Sonos, Logging, time_check, USB_iPhone
import time

cloud = iCloud()
player = Sonos()
log = Logging()

old = None

while True:
    
    player.check_is_playing()
    if not player.is_playing and time_check(hour = 23, minute = 15):
        log.write("Not Playing Check Passed")
        cloud.update_phone()
            
        if cloud.is_home():
            log.write("Is Home Check Passed")
            
            player.check_is_playing()
            #if cloud.is_charging() and player.is_playing:
            if USB_iPhone() and not player.is_playing:
                log.write("All tests passed! Music Started Playing!")
                player.play_fresh()
    else:
        if player.is_playing:
            current = player.current_track()
            if current != old:
                if current == "":
                    log.write("Ad detected, volume turned down")
                    player.set_volume(0)
                else:
                    log.write("Now Playing {}".format(current))
                    if player.volume != player.desired_volume:
                        log.write("Ad done playing, turned volume back to desired")
                        player.ramp_volume()
                old = current

    time.sleep(5)
    # print("TICK")