#!/usr/bin/env python3

import os
import sys
import signal
from argparse import ArgumentParser

# convert read logfile into n-tupel (python list) for easier visualization
# -> use pyqtgraph as a widget for prototyping
#TODO: match read timestamp with system timestamp


class LogReader:
    def __init__(self, logfile):
        self.logfile = logfile

    def __del__(self):
        pass

    # Timestamp:
    # %4d-%2d-%2d[:space:]*%2d:%2d:%2d\.[0-9]*[:space:]

    def readTimestamp(self):
        pass

    def readStrokeStrength(self):
        pass

    def readStrokeCount(self):
        pass

    def readHeartRate(self):
        pass

    def readDistance(self):
        pass

    def readAverageSpeed(self):
        pass

    # returns a list of log entries
    def read(self):
        print( "%s" % self.logfile )
        self.readTimestamp()
        self.readStrokeStrength()
        self.readStrokeCount()
        self.readHeartRate()
        self.readDistance()
        self.readAverageSpeed()


def signal_handler(signal, frame):
    sys.exit(0)
    
    
signal.signal( signal.SIGINT, signal_handler) 


parser = ArgumentParser(description='Parse Waterrower rowing datalogs')
parser.add_argument('logfile', metavar='logfile', help='the logfile to read')


args = parser.parse_args()

if not os.path.exists(args.logfile):
    print('Invalid logfile given!')
    sys.exit(0)

reader = LogReader(args.logfile)    
reader.read()
