# -*- coding: utf-8 -*-
"""
Created on Sat May 15 13:26:53 2021

@author: Schmuck
"""

from pyicloud import PyiCloudService
import sys, os, subprocess
import datetime, time
import soco, warnings

class Logging:
    
    def __init__(self, path = "log.txt"):
        self.path = path
        if path not in os.listdir(os.getcwd()):
            self.__create_file()
        # self.log = self.write_to_log(path)
    
    def formatted_time(self):
        format_time = lambda x: x.strftime("%H:%M:%S %m-%d-%Y")
        return format_time(datetime.datetime.now())
    
    #Create file method, to be used only if needed.
    def __create_file(self):
        with open(self.path, "w") as f:
            f.close()   
        self.write_to_log("Beginning of Log")
    
    def write_to_log(self, message, action = "GENERIC", to_print = False):
        if self.path not in os.listdir(os.getcwd()):
            self.__create_file()
            
        if to_print:
            print(message)
            
        with open(os.getcwd() + "/{}".format(self.path), "a") as f:
            f.write("\n{action}:{date} --> {message}".format(action = action, date = self.formatted_time(), message = message))
            f.close() 

class Sonos:
    
    def __init__(self, desired_volume = 11):
        
        warnings.simplefilter("ignore", UserWarning)
        
        self.__device = soco.discovery.any_soco()
        favorites = self.__device.get_sonos_favorites()
        self.__radio = favorites["favorites"][2]["uri"]
        self.desired_volume = desired_volume
        self.volume = self.__device.volume
        self.is_playing = False
        self.check_is_playing()

    def play_fresh(self):
        self.ramp_volume()
        self.__device.play_uri(self.__radio)
        self.is_playing = True
    
    def play(self):
        self.ramp_volume()
        self.__device.play()
        self.is_playing = True
    
    def stop(self):
        self.__device.stop()
        self.is_playing = False
    
    def ramp_volume(self):
        self.__device.volume = 0
        self.__device.ramp_to_volume(self.desired_volume)    
        
    def set_volume(self, value):
        self.__device.volume = value
    
    def check_is_playing(self):
        self.volume = self.__device.volume
        state = self.__device.get_current_transport_info()
        self.is_playing = state["current_transport_state"] == "PLAYING"
        
    def current_track(self):
        return self.__device.get_current_track_info()["title"]

class iCloud:
    
    def __init__(self):
        creds = self.__load_creds(os.getcwd() + "/Secrets.txt")
        self.api = PyiCloudService(creds[0], creds[1])
        self.__two_factor_routine()
        self.phone = self.Phone()
        self.update_phone()
        
        self.lats, self.longs = self.__load_location()
        
    def __load_location(self):
        with open("location.txt", "r") as f:
            temp = f.readlines()
        out = []
        for i in temp:
            i = i.strip()
            i = i.split(",")
            out.append([float(j) for j in i])
        return out[0], out[1]
            
    
    def update_phone(self):
        _phone = self.api.devices[1]
        status = _phone.status()
        self.phone.update(_phone.content, status)
        
    def __load_creds(self, path):
        with open(path, "r") as f:
            creds = f.readlines()
        return [i.strip() for i in creds]
      
    # Not my code. This was ripped from pycloud docs.
    def __two_factor_routine(self):
        if self.api.requires_2fa:
            print("Two-factor authentication required.")
            code = input("Enter the code you received of one of your approved devices: ")
            result = self.api.validate_2fa_code(code)
            print("Code validation result: %s" % result)
        
            if not result:
                print("Failed to verify security code")
                sys.exit(1)
        
            if not self.api.is_trusted_session:
                print("Session is not trusted. Requesting trust...")
                result = self.api.trust_session()
                print("Session trust result %s" % result)
        
                if not result:
                    print("Failed to request trust. You will likely be prompted for the code again in the coming weeks")
        elif self.api.requires_2sa:
            import click
            print("Two-step authentication required. Your trusted devices are:")
        
            devices = self.api.trusted_devices
            for i, device in enumerate(devices):
                print("  %s: %s" % (i, device.get('deviceName',
                    "SMS to %s" % device.get('phoneNumber'))))
        
            device = click.prompt('Which device would you like to use?', default=0)
            device = devices[device]
            if not self.api.send_verification_code(device):
                print("Failed to send verification code")
                sys.exit(1)
        
            code = click.prompt('Please enter validation code')
            if not self.api.validate_verification_code(device, code):
                print("Failed to verify verification code")
                sys.exit(1)
                
    def is_charging(self):
        first = self.api.devices[1].status()["batteryLevel"]
        count = 0
        
        while True:
            time.sleep(20)
            second = self.api.devices[1].status()["batteryLevel"]
            print("First {} --> Second {}".format(first, second))
            if second != first:
                break
            count += 1
        if second - first > 0.0:
            return True
        else:
            return False
        
    def is_home(self):
        lat_fence = self.lats
        long_fence = self.longs
        
        lat_check = self.phone.location[0] > lat_fence[0] and self.phone.location[0] < lat_fence[1]
        long_check = self.phone.location[1] < long_fence[0] and self.phone.location[1] > long_fence[1]
        return lat_check and long_check
        
    class Phone:
        def __init__(self):
            self.battery = 0.0
            self.location = []
            self.id = ""
            self.timestamp = None
        
        def update(self, content, status):
            self.timestamp = datetime.datetime.now()
            self.battery = status["batteryLevel"]
            self.id = content["id"]
            lat = content["location"]["latitude"]
            long = content["location"]["longitude"]
            self.location = [lat, long]
            
def USB_iPhone():
    command = subprocess.Popen(["lsusb"], stdout = subprocess.PIPE, shell = True)
    (out, err) = command.communicate()
    devices = out.decode("utf-8").split("\n")
    for i in devices:
        name = i.split(" ")[-1][:6]
        if name == "iPhone":
            return True
    return False           
            
def time_check(hour, minute):
    # Night time 23 hour, 15 min
    # Day time 6 hour, 30 min
    now_time = datetime.datetime.now().time()
    test_time = datetime.time(hour = hour, minute = minute)
    return now_time > test_time