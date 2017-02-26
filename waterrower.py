
#!/usr/bin/env python3
import serial
import time
from datetime import datetime
import re
import signal
import sys

class Waterrower:
    def __init__(self, serport ):
        self.serialport = serport
        self.serialport.write(b'USB\r\n')
        self.heartrate = 0
        self.totalspeed = 0
        self.averagespeed = 0
        self.strokecount = 0
        self.distance = 0
        self.display_hours = 0
        self.display_minutes = 0
        self.display_seconds = 0
        self.display_tenthseconds = 0
        self.calories_watts = 0
        self.calories_total = 0
        self.calories_up = 0

    def __del__(self):
        #self.serialport.write(b'EXIT\r\n')
        pass

    def parseStrokeCount(self, msg):
        self.strokecount = int(msg, 16)
        
    def parseTotalSpeed(self, msg):
        self.totalspeed = int(msg, 16)

    def parseAverageSpeed(self, msg):
        self.averagespeed = int(msg,16)
        
    def parseDistance(self, msg):
        self.distance = int(msg,16)

    def parseHeartRate(self, msg):
        self.heartrate = int(msg,16)
        
    def parseDisplayHour(self, msg):
        self.display_hours = int(msg)
    
    def parseDisplayMinutes(self, msg): 
        self.display_minutes = int(msg)

    def parseDisplaySeconds(self, msg):
        self.display_seconds = int(msg)

    def parseDisplayTenthSeconds(self, msg):
        self.display_tenthseconds = int(msg)

    def parseCaloriesWatts(self, msg):
        self.calories_watts = int(msg, 16)

    def parseCaloriesTotal(self, msg):
        self.calories_total = int(msg, 16)

    def parseCaloriesUp(self, msg):
        self.calories_up = int(msg,16)
        
    def plot(self):
        print( "%s | Tm: %02d:%02d:%02d.%d | HR: %s [bpm]  Dist: %s [m]  Strk: %s  Avg: %s [m/s]  Tot: %s |  CalW: %s  TotCal: %s CalUp: %s" %
               (datetime.today().isoformat(' '),
                self.display_hours,
                self.display_minutes,
                self.display_seconds,
                self.display_tenthseconds,
                self.heartrate,
                self.distance,
                self.strokecount,
                self.averagespeed,
                self.totalspeed,
                self.calories_watts,
                self.calories_total,
                self.calories_up))
        
    def parse(self, lines):
        for line in lines:
            line = line.replace(b'\r\n', b'')
            if re.search(b'^IDD140', line):
                self.parseStrokeCount(line[6:])
            elif re.search(b'^IDD148', line):
                self.parseTotalSpeed(line[6:])
            elif re.search(b'^IDD14A', line):
                self.parseAverageSpeed(line[6:])
            elif re.search(b'^IDD057', line):
                self.parseDistance(line[6:])
            elif re.search(b'^IDS1A', line):
                self.parseHeartRate(line[5:])
            elif re.search(b'^IDS1E3', line):
                self.parseDisplayHour( line[6:])
            elif re.search(b'^IDS1E2', line):
                self.parseDisplayMinutes( line[6:])
            elif re.search(b'^IDS1E1', line):
                self.parseDisplaySeconds( line[6:])
            elif re.search(b'^IDS1E0', line):
                self.parseDisplayTenthSeconds( line[6:] )
            elif re.search(b'^IDD088', line):
                self.parseCaloriesWatts( line[6:] )
            elif re.search(b'^IDD08A', line):
                self.parseCaloriesTotal( line[6:] )
            elif re.search(b'^IDS08C', line):
                self.parseCaloriesUp( line[6:] )

    def requestStrokeCount(self):
        self.serialport.write(b'IRD140\r\n')

    def requestTotalSpeed(self):
        self.serialport.write(b'IRD148\r\n')
        
    def requestAverageSpeed(self):
        self.serialport.write(b'IRD14A\r\n')

    def requestDistance(self):
        self.serialport.write(b'IRD057\r\n')

    def requestHeartRate(self):
        self.serialport.write(b'IRS1A0\r\n')

    def requestTime(self):
        self.serialport.write(b'IRS1E3\r\n')
        self.serialport.write(b'IRS1E2\r\n')
        self.serialport.write(b'IRS1E1\r\n')
        self.serialport.write(b'IRS1E0\r\n')

    def requestCaloriesWatts(self):
        self.serialport.write(b'IRD088\r\n')
        
    def requestCaloriesTotal(self):
        self.serialport.write(b'IRD08A\r\n')
        self.serialport.write(b'IRS08C\r\n')


def signal_handler(signal, frame):
    sys.exit(0)

signal.signal( signal.SIGINT, signal_handler) 
        
with serial.Serial('/dev/tty.usbmodem14111', 19200, timeout=0.01 ) as ser:
    waterrower = Waterrower(ser)
    while True:
        waterrower.requestStrokeCount()
        waterrower.requestTotalSpeed()
        waterrower.requestAverageSpeed()
        waterrower.requestDistance()
        waterrower.requestHeartRate()
        waterrower.requestTime()
        waterrower.requestCaloriesWatts()
        waterrower.requestCaloriesTotal()
        waterrower.parse( ser.readlines() )
        waterrower.plot()
        time.sleep(0.03)
