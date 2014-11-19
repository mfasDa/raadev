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
        result.Add(self.__MCtruth)
        for hist in self.__triggers.itervalues():
            result.Add(hist)
        return result

class MonteCarloWriter(object):
    '''
    Class Writing projected raw spectrum and MC truth 
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.__weights = TH1D("weights", "Pythia weights", 11, -0.5, 10.5)
        self.__inputcol = self.ReadData()
        self.__pthardbins = {}
        self.__inAcceptance = False
        
    def SetInAcceptance(self):
        self.__inAcceptance = True
        
    def SetAll(self):
        self.__inAcceptance = False

    def ReadData(self):
        reader = MonteCarloFileHandler(True)
        for pthardbin in range(1,10):
            reader.AddFile("%02d/AnalysisResults.root" %(pthardbin), pthardbin)
        return reader.GetCollection()
        
    def Convert(self):
        for mybin in range(1,10):
            self.ProcessBin(mybin)
        
    def ProcessBin(self, mybin):
        self.__weights.SetBinContent(mybin, self.__inputcol.GetWeigthHandler().GetWeight(mybin))
        results = BinContent()
        bindata = self.__inputcol.GetData(mybin)
        results.SetMCtruth(self.ProjectMCtruth(bindata.GetMCTruth(), "MCTruthBin%d" %(mybin)))
        for trigger in ["MinBias","EMCJHigh","EMCJLow","EMCGHigh","EMCGLow"]:
            tc = bindata.GetData(trigger).FindTrackContainer("tracksWithClusters" if self.__inAcceptance else "tracksAll")
            sn = "%sbin%d" %(trigger, mybin)
            spectrum = self.Project(tc, sn)
            results.AddTrigger(trigger, spectrum)
        self.__pthardbins[mybin] = results
    
    def ProjectMCtruth(self, inputcontainer, outputname):
        inputcontainer.ApplyCut(3,-10., 10.)
        inputcontainer.ApplyCut(4, 1, 1)
        return inputcontainer.ProjectToDimension(0, outputname)

    def Project(self, inputcontainer, outputname):
        inputcontainer.SetVertexRange(-10., 10.)
        inputcontainer.SetPileupRejection(True)
        inputcontainer.SelectTrackCuts(1)
        return inputcontainer.MakeProjection(0, outputname, doNorm = False)
        
    def WriteResults(self):
        outputfile = TFile("MonteCarloProjected%s.root" %("Acc" if self.__inAcceptance else "All"), "RECREATE")
        outputfile.cd()
        self.__weights.Write(self.__weights.GetName(), TObject.kSingleKey)
        for mybin in self.__pthardbins:
            bindata = self.__pthardbins[mybin].MakeROOTPrimitive("bin%d" %(mybin))
            bindata.Write(bindata.GetName(), TObject.kSingleKey)
        outputfile.Close()
        
def RunProjection(doAcc = False):
    writer = MonteCarloWriter()
    if doAcc:
        writer.SetInAcceptance()
    else:
        writer.SetAll()
    writer.Convert()
    writer.WriteResults()