
class StrokePhase:
    def __init__(self):
        self.logentries = []

    def addLogEntry(self, entry):
        self.logentries.append( entry )

    def plot(self):
        print("StrokePhase:")
        for i in self.logentries:
            i.plot()