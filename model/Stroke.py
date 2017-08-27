
from model.LogEntry import LogEntry
from model.RecoveryPhase import RecoveryPhase
from model.StrokePhase import StrokePhase

class Stroke:

    def __init__(self, strokeID ):
        self.strokeID = strokeID
        self.strokePhase = StrokePhase()
        self.recoveryPhase = RecoveryPhase()

    def addLogEntry(self, entry):
        if isinstance( entry, LogEntry ):
            if entry.isStroke():
                self.strokePhase.addLogEntry( entry )
            else:
                self.recoveryPhase.addLogEntry( entry )

    def getStrokeID(self):
        return self.strokeID

    def plot(self):
        print( "\n\nStroke %d\n" % self.strokeID)
        self.strokePhase.plot()
        self.recoveryPhase.plot()