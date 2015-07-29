'''
Created on Nov 24, 2014

Calculate fraction of min bias events which are also triggered by the min. bias trigger

@author: markus
'''

from ROOT import TFile, TH1D
from ROOT import gDirectory, gROOT

triggerlookup = {"MinBias":0, "EMCJHigh":1, "EMCJLow":2, "EMCGHigh":3, "EMCGLow":4}

def GetTriggerScalers(filename):
    inputfile = TFile.Open(filename)
    inputfile.cd("PtEMCalTriggerTask")
    gDirectory.ls()
    tasklist = gDirectory.Get("results")
    histlist = tasklist.FindObject("histosPtEMCalTriggerHistograms")
    gROOT.cd()
    triggerhist = histlist.FindObject("hEventTriggers")
    inputfile.Close()
    
    # Get number of Min. Bias counts
    mbcounts = GetCounts(triggerhist, "MinBias")
    print "MinBias counts: %d" %(mbcounts)

    triggerhist.GetAxis(0).SetRange(2,2)
    triggercounts = {}
    for trigger in triggerlookup.keys():
        if trigger == "MinBias":
            continue
        triggercounts[trigger] = GetCounts(triggerhist, trigger)
        print "Number of events for trigger %s: %d" %(trigger, triggercounts[trigger])
    
    hScalers = TH1D("triggerScalers", "trigger scalers", len(triggercounts), -0.5, len(triggercounts) - 0.5)
    counter = 1
    for trigger in triggercounts.keys():
        scaler = float(mbcounts)/float(triggercounts[trigger])
        print "Scaler for trigger %s: %f" %(trigger, scaler)
        hScalers.GetXaxis().SetBinLabel(counter, trigger)
        hScalers.SetBinContent(counter, scaler)
        counter += 1
        
    outputfile = TFile("TriggerScalers.root", "RECREATE")
    outputfile.cd()
    hScalers.Write()
    outputfile.Close()
    
def GetCounts(triggerhist, triggerclass):
    projection = triggerhist.Projection(triggerlookup[triggerclass])
    return projection.GetBinContent(2)