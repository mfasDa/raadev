'''
Created on Nov 17, 2014

@author: markus
'''

from ROOT import TFile,TH1D,TList,TObject

from base.MonteCarloFileHandler import MonteCarloFileHandler
from __builtin__ import True

class BinContent(object):
    
    def __init__(self):
        self.__MCtruth = None
        self.__triggers = {}
        
    def SetMCtruth(self, mctruth):
        self.__MCtruth = mctruth
        
    def AddTrigger(self, triggername, spectrum):
        self.__triggers[triggername] = spectrum
        
    def MakeROOTPrimitive(self, name):
        result = TList()
        result.SetName(name)
        if self.__MCtruth:
            result.Add(self.__MCtruth)
        for hist in self.__triggers.itervalues():
            result.Add(hist)
        return result
    
class MonteCarloWriter(object):
    
    def __init__(self):
        '''
        Constructor
        '''
        self._weights = TH1D("weights", "Pythia weights", 11, -0.5, 10.5)
        self._inputcol = self.ReadData()
        self._pthardbins = {}

    def ReadData(self):
        reader = MonteCarloFileHandler(True)
        for pthardbin in range(1,10):
            reader.AddFile("%02d/AnalysisResults.root" %(pthardbin), pthardbin)
        return reader.GetCollection()

    def Convert(self):
        for mybin in range(1,10):
            self._weights.SetBinContent(mybin, self._inputcol.GetWeigthHandler().GetWeight(mybin))
            self._pthardbins[mybin] = self.ProcessBin(mybin)
            
    def WriteResults(self):
        outputfile = TFile(self.CreateOutputFilename(), "RECREATE")
        outputfile.cd()
        self._weights.Write(self._weights.GetName(), TObject.kSingleKey)
        for mybin in self._pthardbins:
            bindata = self._pthardbins[mybin].MakeROOTPrimitive("bin%d" %(mybin))
            bindata.Write(bindata.GetName(), TObject.kSingleKey)
        outputfile.Close()
        
    # pure virtual methods:
    def CreateOutputFilename(self):
        pass
    
    def ProcessBin(self, mybin):
        pass

class TrackWriter(MonteCarloWriter):
    '''
    Class Writing projected raw spectrum and MC truth 
    '''

    def __init__(self):
        '''
        Constructor
        '''
        MonteCarloWriter.__init__(self)
        self.__inAcceptance = False
        self.__MCKine = False
        
    def SetInAcceptance(self):
        self.__inAcceptance = True
        
    def SetAll(self):
        self.__inAcceptance = False
        
    def SetMCKine(self):
        self.__MCKine = True
        
    def SetRecKine(self):
        self.__MCKine = False
        
    def ProcessBin(self, mybin):
        results = BinContent()
        bindata = self._inputcol.GetData(mybin)
        results.SetMCtruth(self.ProjectMCtruth(bindata.GetMCTruth(), "MCTruthBin%d" %(mybin)))
        kinestring = "tracksMCKine" if self.__MCKine else "tracks"
        acceptancestring = "WithClusters" if self.__inAcceptance else "All"
        for trigger in ["MinBias","EMCJHigh","EMCJLow","EMCGHigh","EMCGLow"]:
            histname = "%s%s" %(kinestring, acceptancestring)
            print "histname: %s" %(histname)
            tc = bindata.GetData(trigger).FindTrackContainer(histname)
            sn = "%sbin%d" %(trigger, mybin)
            spectrum = self.Project(tc, sn)
            results.AddTrigger(trigger, spectrum)
        return results
    
    def CreateOutputFilename(self):
        return "MonteCarloProjected%s%sKine.root" %("Acc" if self.__inAcceptance else "All", "MC" if self.__MCKine else "Rec")
    
    def ProjectMCtruth(self, inputcontainer, outputname):
        inputcontainer.ApplyCut(3,-10., 10.)
        inputcontainer.ApplyCut(4, 1, 1)
        return inputcontainer.ProjectToDimension(0, outputname)

    def Project(self, inputcontainer, outputname):
        inputcontainer.SetVertexRange(-10., 10.)
        inputcontainer.SetPileupRejection(True)
        inputcontainer.SelectTrackCuts(1)
        return inputcontainer.MakeProjection(0, outputname, doNorm = False)
        
        
class ClusterWriter(MonteCarloWriter):
    
    def __init__(self):
        MonteCarloWriter.__init__(self)
        self.__calibrated = True
        
    def SetCalibrated(self):
        self.__calibrated = True
    
    def SetUncalibrated(self):
        self.__calibrated = False
        
    
    def ProcessBin(self, pthatbin):
        """
        Make projections of the different cluster hists
        """
        results = BinContent()
        bindata = self._inputcol.GetData(pthatbin)
        for trigger in ["MinBias","EMCJHigh","EMCJLow","EMCGHigh","EMCGLow"]:
            clustercont = bindata.GetData(trigger).FindClusterContainer("Calib" if self.__calibrated else "Uncalib")
            spectrum = self.ProjectContainer(clustercont, "%sbin%d" %(trigger, pthatbin))
            results.AddTrigger(trigger, spectrum)
        return results

    def ProjectContainer(self, inputcontainer, outputname):
        inputcontainer.SetVertexRange(-10, 10)
        inputcontainer.SetPileupRejection(True)
        return inputcontainer.MakeProjection(0, outputname, doNorm = False)
    
    def CreateOutputFilename(self):
        return "MonteCarloClusterProjection%s.root" %("Calib" if self.__calibrated else "Uncalib")

        
def RunTrackProjection(doAcc = False, doMCKine = False):
    writer = TrackWriter()
    if doAcc:
        writer.SetInAcceptance()
    else:
        writer.SetAll()
    if doMCKine:
        writer.SetMCKine()
    else:
        writer.SetRecKine()
    writer.Convert()
    writer.WriteResults()
    
def RunClusterProjection(doCalib = True):
    writer = ClusterWriter()
    if doCalib:
        writer.SetCalibrated()
    else:
        writer.SetUncalibrated()
    writer.Convert()
    writer.WriteResults()