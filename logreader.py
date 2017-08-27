#!/usr/bin/env python3

import os
import sys
import signal
import re
import datetime
import difflib
from argparse import ArgumentParser
from model.LogEntry import LogEntry
from model.Stroke import Stroke

# convert logfile into n-tupel (python list) for easier visualization
# -> use pyqtgraph ast a widget for prototyping
#TODO: match read timestamp with system timestamp


class LogReader:
    def __init__(self, logfile):
        self.logfile = logfile

    def __del__(self):
        pass

    def parseHour(self, hour_str):
        if re.compile("^[0-9]{1,2}$").search(hour_str):
            return int(hour_str)
        return None

    def parseMinute(self, minute_str):
        if re.compile("^[0-9]{1,2}$").search(minute_str):
            return int(minute_str)
        return None

    def parseSecond( self, second_str ):
        if re.compile("^[0-9]{1,2}\.[0-9]*$").search(second_str) != None:
            microsecond = 0
            second = int(float(second_str))
            second_split = second_str.split('.')
            if len(second_split) > 1:
                microsecond_str = second_split[1]
                microsecond = int(microsecond_str) * pow( 10, 6-len(microsecond_str) )
            return (second, microsecond)
        elif re.compile("^[0-9]{1,2}$").search(second_str) != None:
            return (int(second_str),0)
        return None


    # Timestamp:
    # %4d-%2d-%2d[:space:]*%2d:%2d:%2d\.[0-9]*[:space:]

    def readHostTime(self, timestamp):
        splitted=timestamp.split()
        date = None
        time = None
        filteredTimestamp = None
        if len(splitted) > 1 :
            date_str = splitted[0]
            date_splitted = date_str.split("-")
            if len(date_splitted) > 2:
                year_str = date_splitted[0]
                month_str = date_splitted[1]
                day_str = date_splitted[2]
                if re.compile("^[0-9]{4}$").search( year_str ) != None:
                    year = int(year_str)
                    if re.compile("^[0-9]{1,2}$").search(month_str) != None:
                        month = int(month_str)
                        if re.compile("^[0-9]{1,2}$").search(day_str) != None:
                            day = int(day_str)
                            date = datetime.date( year, month, day)
            time_str = splitted[1]
            time_splitted = time_str.split(":")
            if len(time_splitted) > 2:
                hour_str = time_splitted[0]
                minute_str = time_splitted[1]
                second_str = time_splitted[2]
                hour = self.parseHour( hour_str )
                if hour != None:
                    minute = self.parseMinute( minute_str )
                    if minute != None:
                        second = self.parseSecond( second_str )
                        if second != None:
                            time = datetime.time( hour=hour, minute=minute, second=second[0], microsecond=second[1] )
        if date != None and time != None:
            filteredTimestamp = datetime.datetime.combine( date, time )
        if filteredTimestamp != None:
            timestamp=timestamp.replace(" ", "")
            converted_str=filteredTimestamp.isoformat(' ').replace(" ","")
            if converted_str == timestamp:
                return filteredTimestamp
            print(converted_str)
            print(sys.stdout.writelines(difflib.context_diff(timestamp, converted_str)))
            print("\nTimestamp:\n\tActual: \t%s\n\tConverted:\t%s" % (timestamp, converted_str))
        print(timestamp)
        return None

    def readDisplayTime(self, rowingtime):
        filteredRowingTime=None
        splitted_rawstring=rowingtime.split()
        if len(splitted_rawstring) > 1:
            rowingtime_str = splitted_rawstring[1].replace(" \n\r","")
            rowingtime_splitted = rowingtime_str.split(":")
            if len(rowingtime_splitted) > 2:
                hour_str = rowingtime_splitted[0]
                hour = self.parseHour( hour_str )
                if hour != None:
                    minute_str = rowingtime_splitted[1]
                    minute = self.parseMinute( minute_str )
                    if minute != None:
                        second_str = rowingtime_splitted[2]
                        second = self.parseSecond( second_str )
                        if second != None:
                            filteredRowingTime = datetime.time( hour=hour, minute=minute, second=second[0], microsecond=second[1] )

        if filteredRowingTime != None:
            filteredTime=filteredRowingTime.isoformat( timespec='milliseconds').replace(" \r\n", "")
            filteredTime=filteredTime[:len(filteredTime)-2]
            if filteredTime == rowingtime_str:
                return filteredRowingTime
            print(rowingtime_str)
            print(filteredTime)
            print(sys.stdout.writelines(difflib.context_diff(rowingtime_str, filteredTime)))
            print("\nRowingTime:\n\tActual: \t%s\n\tConverted:\t%s" % (rowingtime, filteredTime))
            # grep -o Tm.\*\|.StrkSt | cut -f2  -d\
        return None
    # how to proceed from here:
    #
    # - display time holds the 00:00:00 mark somewhere -> find the line, where it first occures and take the hosttime
    # - data model may be error prone -> larger time differences should be unsharpely detected by correlation, but how?
    # - calculate time difference between 00:00:00 hosttime and current hosttime and match it with current display time
    # -> should work, milliseconds should be irrelevant
    # but: how to proceed with larger errors in display time, seems like a nearly random process
    # calculate likeliness of current displaytime compared to previous line?
    # -> noch nicht sicher, gucken
    # eventuell sogar noch besser, die Haeufigkeiten zu matchen
    
    def isStrokeActive(self, stroking):
        regex = re.compile("StrkSt:.[0-9]*")
        if regex.search( stroking ) != None:
            list = stroking.split(':')
            if len(list) > 0:
                strokeActive = int( list[1] )
                validationString =":".join( [list[0], " %d " % strokeActive  ] )
                if stroking == validationString:
                    return strokeActive
                print( "len(stroking)=%d len(validationString)=%d" % (len(stroking), len(validationString)))
                print(stroking)
                print(validationString)
                print(sys.stdout.writelines(difflib.context_diff(stroking, validationString)))
                print("\nStroking:\n\tActual: \t%s\n\tConverted:\t%d" % (stroking, strokeActive))
        return None

    def readStrokeCount(self, strokeCount_raw):
        strokeCount_raw=strokeCount_raw.replace(" ", "")
        regex = re.compile("Strk:[0-9]*")
        if regex.search( strokeCount_raw ) != None:
            strokeCount_splitted=strokeCount_raw.split(':')
            if len(strokeCount_splitted) > 1:
                strokeCount = int(strokeCount_splitted[1])
                validationString = ":".join([ strokeCount_splitted[0], "%d" % strokeCount])
                if strokeCount_raw == validationString:
                    if strokeCount > 0:
                        return strokeCount
                    return None
                print("len(strokeCount)=%d len(validationString)=%d" % (len(strokeCount_raw), len(validationString)))
                print("\nStrokeCount:\n\tActual: \t%s\n\tConverted:\t%d" % (strokeCount_raw, strokeCount))
        return None

    def readHeartRate(self, heartRate_raw):
        heartRate_raw=heartRate_raw.replace(" ", "")
        regex = re.compile( "HR:[0-9]*\[bpm\]" )
        if regex.search( heartRate_raw ) != None:
            heartrate_splitted_no_prefix=heartRate_raw.split(":")
            if len(heartrate_splitted_no_prefix) > 1:
                heartrate_splitted_no_suffix = heartrate_splitted_no_prefix[1].split("[")
                if len(heartrate_splitted_no_suffix) > 1:
                    heartrate = int(heartrate_splitted_no_suffix[0])
                    validationString = "HR:%d[bpm]" % heartrate
                    if heartRate_raw == validationString:
                        return heartrate
            print("\nHeartRate:\n\tActual: \t%s\n\tConverted:\t%d" % (heartRate_raw, heartRate) )
        return None

    def readDistance(self, distance_raw):
        distance_raw=distance_raw.replace(" ", "")
        regex = re.compile("Dist:[0-9]*\[m\]")
        if regex.search(distance_raw) != None:
            distance_splitted_no_prefix = distance_raw.split(":")
            if len(distance_splitted_no_prefix) > 1:
                distance_splitted_no_suffix=distance_splitted_no_prefix[1].split("[")
                if len(distance_splitted_no_suffix) > 1:
                    distance = int(distance_splitted_no_suffix[0])
                    validationString = "Dist:%d[m]" % distance
                    if distance_raw == validationString:
                        return distance
                    print("\nDistance:\n\tActual: \t%s\n\tConverted:\t%d" % (distance_raw, distance))
        return None

    def readAverageSpeed(self, averageSpeed_raw ):
        averageSpeed_raw=averageSpeed_raw.replace(" ", "")
        regex = re.compile("Avg:[0-9]*\[m/s\]")
        if regex.search(averageSpeed_raw) != None:
            averageSpeed_splitted_no_prefix = averageSpeed_raw.split(":")
            if len(averageSpeed_splitted_no_prefix) > 1:
                averageSpeed_splitted_no_suffix=averageSpeed_splitted_no_prefix[1].split("[")
                if len(averageSpeed_splitted_no_suffix) > 1:
                    averageSpeed = int(averageSpeed_splitted_no_suffix[0])
                    validationString = "Avg:%d[m/s]" % averageSpeed
                    if averageSpeed_raw == validationString:
                        return averageSpeed
                    print("\nAverageSpeed:\n\tActual: \t%s\n\tConverted:\t%s" % (averageSpeed_raw, averageSpeed_raw))
        return None

    def readTotalSpeed(self, totalSpeed_raw ):
        totalSpeed_raw=totalSpeed_raw.replace(" ", "")
        regex = re.compile("Tot:[0-9]*")
        if regex.search(totalSpeed_raw) != None:
            totalSpeed_split = totalSpeed_raw.split(':')
            if len(totalSpeed_split) > 0:
                totalSpeed = int( totalSpeed_split[1] )
                validationString = "Tot:%d" % totalSpeed
                if totalSpeed_raw == validationString:
                    return totalSpeed
                print("\nTotalSpeed:\n\tActual: \t%s\n\tConverted:\t%d" % (totalSpeed_raw, totalSpeed))
        return None

    def readCaloriesWorked(self, calories_raw):
        calories_raw=calories_raw.replace(" ","")
        regex = re.compile("CalW:[0-9]*")
        if regex.search(calories_raw) != None:
            calories_split = calories_raw.split(':')
            if len(calories_split) > 0:
                calories = int(calories_split[1])
                validationString = "CalW:%d" % calories
                if calories_raw == validationString:
                    return calories
                print("\nCalories:\n\tActual: \t%s\n\tConverted:\t%d" % (calories_raw, calories))
        return None

    def readCaloriesTotal(self, totalCalories_raw):
        totalCalories_raw = totalCalories_raw.replace("\n", "").replace('\r', "")
        calories_splitted=totalCalories_raw.split("CalUp: ")
        if len(calories_splitted) > 1:
            totalCalories_upper = int( calories_splitted[1] )
            totalCalories_lower = int( calories_splitted[0].replace('TotCal: ', '') )
            totalCalories_str = "TotCal: %d CalUp: %d" % (totalCalories_lower, totalCalories_upper)
            if totalCalories_str == totalCalories_raw:
                return (totalCalories_upper, totalCalories_lower)
            print(totalCalories_str)
            print(totalCalories_raw)
            print(totalCalories_upper)
            print(totalCalories_lower)
            #print("\nCalories:\n\tActual: \t%s\n\tConverted:\t%s" % (calories, calories))
        return None

    # returns a list of log entries
    def read(self):
        with open(self.logfile) as f:
            lines = f.readlines()
            currentStroke = Stroke(0)
            for line in lines:
                splitLine = line.split('|')
                timestamp = splitLine[0]
                rowingtime = splitLine[1]
                stroking = splitLine[2]
                workout = splitLine[3]
                workout_splitted = workout.split("  ")
                heartRate = workout_splitted[0]
                distance = workout_splitted[1]
                strokeCount = workout_splitted[2]
                averageSpeed = workout_splitted[3]
                totalSpeed = workout_splitted[4]
                calories = splitLine[4]
                calories_splitted = calories.split('  ')
                count = self.readStrokeCount(strokeCount)
                if count != None:
                    if currentStroke.getStrokeID() != count:
                        currentStroke.plot()
                        currentStroke = Stroke( count )
                    entry=LogEntry()
                    entry.setTime(self.readHostTime( timestamp ) )
                    entry.setDisplayTime(self.readDisplayTime( rowingtime ) )
                    entry.setStrokePhase(self.isStrokeActive( stroking ) )
                    entry.setStrokeCount( count )
                    entry.setHeartRate(self.readHeartRate( heartRate ) )
                    entry.setDistance(self.readDistance( distance ) )
                    entry.setAverageSpeed(self.readAverageSpeed( averageSpeed ) )
                    entry.setTotalSpeed(self.readTotalSpeed( totalSpeed ) )
                    entry.setCaloriesWorkedi(self.readCaloriesWorked( calories_splitted[1] ) )
                    entry.setCaloriesTotal(self.readCaloriesTotal( calories_splitted[2] ) )
                    currentStroke.addLogEntry( entry )


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
