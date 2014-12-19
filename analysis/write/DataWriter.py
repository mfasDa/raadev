'''
Created on Dec 18, 2014

@author: markus
'''

from base.FileHandler import LegoTrainFileReader
from ROOT import TFile, TList, TObject, TH1F

class DataSpectra(object):
    
    class TriggerData(object):

        def __init__(self, triggername, events, spec):
            self.__triggername = triggername
            self.__eventcount = events
            self.__projectedSpectrum = spec

        def get_triggername(self):
            return self.__triggername

        def get_eventcount(self):
            return self.__eventcount

        def get_projected_spectrum(self):
            return self.__projectedSpectrum
            
        def set_triggername(self, value):
            self.__triggername = value

        def set_eventcount(self, value):
            self.__eventcount = value

        def set_projected_spectrum(self, value):
            self.__projectedSpectrum = value
    
        def del_eventcount(self):
            del self.__eventcount

        def del_projected_spectrum(self):
            del self.__projectedSpectrum
        
        def del_triggername(self):
            del self.__triggername
    
        def MakeROOTPrimitive(self):
            result = TList()
            result.SetName(self.triggername)
            self.__eventcount.SetName("events")
            self.__projectedSpectrum.SetName("spectrum")
            result.Add(self.__events)
            result.Add(self.__projectedSpectrum)
            return result
    
        eventcount = property(get_eventcount, set_eventcount, del_eventcount, "Histogram with the event selection")
        projectedSpectrum = property(get_projected_spectrum, set_projected_spectrum, del_projected_spectrum, "Histogram with the not-normalised projected spectrum")
        triggername = property(get_triggername, set_triggername, del_triggername, "Name of the trigger class")
    
    def __init__(self):
        self.__triggers = {}

    def get_triggers(self):
        return self.__triggers

    def set_triggers(self, value):
        self.__triggers = value

    def del_triggers(self):
        del self.__triggers

    triggers = property(get_triggers, set_triggers, del_triggers, "Trigger data list")
        
    def AddTrigger(self, triggerName, spectrum, events):
        self.__triggers[triggerName] = self.TriggerData(events, spectrum)
        
    def GetListOfROOTPrimitives(self):
        rootprim = []
        for trigger in self.__triggers.itervalues():
            rootprim.append(trigger.MakeROOTPrimitive())
        return rootprim

class DataWriter(object):
    
    def __init__(self, filename):
        self._inputdata = self.__ReadFile(filename)
        self._outputdata = DataSpectra()
        
    def __ReadFile(self, filename):
        reader = LegoTrainFileReader(filename)
        return reader.ReadFile()
    
    def Convert(self):
        for trigger in ["MinBias", "EMCJhigh", "EMCJLow", "EMCGHigh"]:
            trdata = self._ProcessTrigger(trigger, self._inputdata.GetData(trigger))
            self._outputdata.AddTrigger(trigger, trdata["spectrum"], trdata["events"])
        
    def WriteOutput(self):
        myoutput = TFile(self._GetOutputFile(), "RECREATE")
        myoutput.cd()
        for obj in self._outputdata.GetListOfROOTPrimitives():
            obj.Write(obj.GetName(), TObject.kSingleKey)
        myoutput.Close()
        
    def _MakeProjection(self, trackContainer):
        return trackContainer.MakeProjection("spectrum", 0, doNorm = False)
    
    def _GetNumberOfEvents(self, trackContainer):
        eventHist = TH1F("events", "Events", 1, 0.5, 1.5)
        eventHist.SetBinContent(1, trackContainer.GetEventCount())
        return eventHist
         
    # Pure virtual functions
    def _ProcessTrigger(self, trigger, dset):
        print "Method needs to be implemented by inheriting classes"
        
    def _GetOutputFile(self):
        print "Method needs to be implemented by inheriting classes"
        
class DataTrackWriter(DataWriter):
    
    def __init__(self, filename):
        DataWriter.__init__(self, filename)
        self.__etacut = None
        self.__inAcceptance = False
        
    def SetEtaCut(self, tag, emin, emax):
        self.__etacut = {"etamin":emin, "etamax":emax, "tag":tag}
        
    def SetInAcceptance(self, inAcceptance = True):
        self.__inAcceptance = inAcceptance
        
    def _GetOutputFile(self):
        accString = "All"
        if self.__inAcceptance:
            accString = "InAcceptance"
        etastring = "All"
        if self.__etacut:
            etastring = self.__etacut["tag"]
        return "DataTracks%sEta%s.root" %(accString, etastring)
    
    def __DefineTracks(self, tc):
        tc.SetVertexRange(-10, 10)
        tc.SetPileupRejection()
        tc.SelectTrackCuts(1)
        if self.__etacut:
            tc.SetEtaRange(self.__etacut["etamin"], self.__etacut["etamax"])
    
    def _ProcessTrigger(self, trigger, dset):
        containerName = "tracksAll"
        if self.__inAcceptance:
            containerName = "tracksWithClusters" 
        tc = dset.FindTrackContainer(containerName)
        self.__DefineTracks(tc)
        projected = self._MakeProjection(tc)
        nevents = self._GetNumberOfEvents(tc)
        self._outputdata.AddTrigger(trigger, projected, nevents)

        
class DataClusterWriter(DataWriter): 
    
    def __init__(self, filename):
        DataWriter.__init__(self, filename)
        self.__useCalibrated = True
        
    def SetUseCalibratedClusters(self, doUse = True):
        self.__useCalibrated = doUse
        
    def _GetOutputFile(self):
        calibstring = "Uncalib"
        if self.__useCalibrated:
            calibstring = "Calib"
        return "DataCluster%s.root" %(calibstring)
    
    def _ProcessTrigger(self, trigger, dset):
        containerName = "Uncalib"
        if self.__useCalibrated:
            containerName = "Calib"
        cc = dset.FindTrackContainer(containerName)
        self.__DefineClusters(cc)
        projected = self.__MakeProjection(cc)
        nevents = self.__GetNumberOfEvents(cc)
        self._outputdata.AddTrigger(trigger, projected, nevents)
    
    def __DefineClusters(self, cc):
        cc.SetVertexRange(-10, 10)
        cc.SetPileupRejection()
    
def WriteTracks(filename, inAcceptance = False, etaSel = "all"):
    writer = DataTrackWriter(filename)
    writer.SetInAcceptance(inAcceptance)
    if etaSel == "centcms":
        writer.SetEtaCut(-0.8, -0.3, "centcms")
    writer.Convert()
    writer.WriteOutput()

def WriteClusters(filename, calib = True):
    writer = DataClusterWriter(filename)
    writer.SetUseCalibratedClusters(calib)
    writer.Convert()
    writer.WriteOutput()