#! /usr/bin/env python

from base.FileHandler import LegoTrainFileReader

def Run():
    periods = ["LHC13c", "LHC13d", "LHC13e", "LHC13f", "merged"]
    for period in periods:
        GetNumberOfEventsForPeriod(period)
        
def GetNumberOfEventsForPeriod(period):
    handler = LegoTrainFileReader("%s/AnalysisResults.root" %(period))
    data = handler.ReadFile()
    print "Period %s" %(period)
    for trg in data.GetListOfTriggers():
        PrintEventCountForTrigger(data.GetData(trg).FindTrackContainer("tracksAll"), trg)
        
def PrintEventCountForTrigger(data, trigger):
    data.SetVertexRange(-10, 10)
    data.SetPileupRejection(True)
    print "%s: %d" %(trigger, data.GetEventCount())
    
if __name__ == "__main__":
    Run()