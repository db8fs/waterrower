
import datetime

#
class LogEntry:

    def __init__(self):
        self.timestamp = None
        self.displayTime = None
        self.strokeCount = None
        self.heartRate = None
        self.strokeActive = False
        self.strokeCount = None
        self.heartRate = None
        self.distance = None
        self.averageSpeed = None
        self.totalSpeed = None
        self.caloriesWorked = None
        self.caloriesTotal = None

    # sets the logging date+time
    def setTime(self, timestamp):
        if isinstance( timestamp, datetime.datetime ):
            self.timestamp = timestamp

    # sets the time displayed on the rowing computer
    def setDisplayTime(self, displayTime):
        if isinstance( displayTime, datetime.time ):
            self.displayTime = displayTime

    # sets the stroking or recovery phase (1 - Stroking, 0 - Recovery)
    def setStrokePhase(self, strokeActive):
        if isinstance( strokeActive, int):
            if strokeActive == 0:
                self.strokeActive = False
            else:
                self.strokeActive = True

    def setStrokeCount(self, strokeCount):
        if isinstance( strokeCount, int):
            self.strokeCount = strokeCount

    def setHeartRate(self, heartRate):
        if isinstance( heartRate, int):
            self.heartRate = heartRate

    def setDistance(self, distance):
        if isinstance( distance, int):
            self.distance = distance

    def setAverageSpeed(self, averageSpeed):
        if isinstance(averageSpeed, int):
            self.averageSpeed = averageSpeed

    def setTotalSpeed(self, totalSpeed):
        if isinstance(totalSpeed, int):
            self.totalSpeed = totalSpeed

    def setCaloriesWorked(self, caloriesWorked):
        if isinstance(caloriesWorked, int):
            self.caloriesWorked = caloriesWorked

    def setCaloriesTotal(self, caloriesTotal):
        if isinstance(caloriesTotal, int):
            self.caloriesTotal = caloriesTotal

    def plot(self):
        str = ""
        if self.strokeCount != None:
            if self.timestamp != None:
                str += "%04d-%02d-%02d %02d:%02d:%02d.%1d" % (  self.timestamp.year,
                                                                self.timestamp.month,
                                                                self.timestamp.day,
                                                                self.timestamp.hour,
                                                                self.timestamp.minute,
                                                                self.timestamp.second,
                                                                self.timestamp.microsecond)
            if self.displayTime != None:
                str += "\t%02d:%02d:%02d" % (   self.displayTime.hour,
                                                self.displayTime.minute,
                                                self.displayTime.second)

            if self.strokeCount != None:
                str += "\tStroke: %d" % self.strokeCount
        print(str)

    def isStroke(self):
        return self.strokeActive