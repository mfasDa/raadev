#! /usr/bin/env python

from Helper import ReadHistList
from SpectrumContainer import DataContainer

def Run():
    periods = ["LHC13c", "LHC13d", "LHC13e"]
    for period in periods:
        GetNumberOfEventsForPeriod(period)
        
def GetNumberOfEventsForPeriod(period):
    triggers = ["MinBias","EMCJHigh","EMCJLow","EMCGHigh","EMCGLow"]
    data = ReadSpectra("%s/AnalysisResults.root" %(period), triggers)
    print "Period %s" %(period)
    for trg in triggers:
        PrintEventCountForTrigger(data[trg], trg)
        
def PrintEventCountForTrigger(data, trigger):
    data.SetVertexRange(-10, 10)
    data.SetPileupRejection(True)
    print "%s: %d" %(trigger, data.GetEventCount())
    
def ReadSpectra(filename, triggers):
    """
    Read the spectra for different trigger classes from the root file
    Returns a dictionary of triggers - spectrum container
    """
    hlist = ReadHistList(filename, "PtEMCalTriggerTask")
    result = {}
    for trg in triggers:
        result[trg] = DataContainer(eventHist = hlist.FindObject("hEventHist%s" %(trg)), trackHist = hlist.FindObject("hTrackHist%s" %(trg)))
    return result
