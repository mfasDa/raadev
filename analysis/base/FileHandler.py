#! /usr/bin/env python
"""
FileHandler.py
 Created on: 29.08.2014
     Author: markusfasel
"""

from ROOT import TFile,TIter,TObject,gDirectory,gROOT
from copy import deepcopy
from SpectrumContainer import DataSet, ClusterContainer, TrackContainer, SpectrumContainer
from FileResults import ResultData
    
class FileReader(object):
    
    class FileReaderException(Exception):
        """
        Exception class handling root files which are
        either not found or not readable.
        """

        def __init__(self, filename):
            """
            Constructor, assigning the name of the file which 
            failed to be read.
            """
            self.filename = filename

        def __str__(self):
            """
            Create string representation of the error message
            """
            return "Could not open file %s" %(self.filename)

    
    def __init__(self, filename, isMC = False):
        """
        Initialise file reader with name of the file to read
        """
        self.__filename = filename
        self.__directory = None
        self.__isMC = isMC
        self.__isReadWeights = False
        self.__weightlist = None
        
    def SetReadWeights(self):
        """
        Read also histograms for the weight calculation
        """
        self.__isReadWeights = True
        
    def GetWeightHistograms(self):
        """
        Access to weight histograms
        """
        return self.__weightlist
        
    def SetDirectory(self, dirname):
        """
        Set directory inside the rootfile
        """
        self.__directory = dirname
    
    def ReadFile(self):
        """
        Read rootfile and create a ResultData structure with all the histograms sorted according
        to trigger classes. Raising FileReaderExceptions if the file can't be opened, doesn't contain
        the directory or list, or has an empty histogram list
        """
        filecontent = self.__ReadHistList()
        if self.__isReadWeights:
            self.__weightlist = filecontent["weights"]
        hlist = filecontent["spectra"]
        if not hlist.GetEntries():
            raise self.FileReaderException("Empty list of histograms in file %s" %(self.__filename))
        result = ResultData("result")
        
        # Handle MC-truth data
        if self.__isMC:
            result.SetMCTruth(SpectrumContainer(hlist.FindObject("hMCtrueParticles")))
        
        # build list of histograms and extract trigger names
        histnames = []
        for oID in range(0, hlist.GetEntries()):
            histnames.append(hlist.At(oID).GetName())    
        triggers = []
        for hname in histnames:
            if not "hEventHist" in hname:
                continue
            triggers.append(hname.replace("hEventHist",""))
        print "Found the following triggers:"
        print "================================="
        isFirst = True
        trgstring = ""
        for trg in triggers:
            if isFirst:
                trgstring += trg 
                isFirst = False
            else:
                trgstring += ", %s" %(trg)
        print trgstring
        
        # Add the result hists to the result container
        for trigger in triggers:
            eventhist = hlist.FindObject("hEventHist%s" %(trigger))
            trackhist = hlist.FindObject("hTrackHist%s" %(trigger))
            #eventhist.Sumw2()
            #trackhist.Sumw2()
            triggerdata = DataSet()
            triggerdata.AddTrackContainer("tracksAll", TrackContainer(eventHist = deepcopy(eventhist), trackHist = trackhist))
            tracksWithClusters = hlist.FindObject("hTrackInAcceptanceHist%s" %(trigger)) 
            if tracksWithClusters:
                triggerdata.AddTrackContainer("tracksWithClusters", TrackContainer(eventHist = deepcopy(eventhist), trackHist = tracksWithClusters))
            tracksMCKine = hlist.FindObject("hMCTrackHist%s" %(trigger))
            if tracksMCKine:
                triggerdata.AddTrackContainer("tracksMCKineAll", TrackContainer(eventHist=deepcopy(eventhist), trackHist = tracksMCKine))
            tracksMCKineWithClusters = hlist.FindObject("hMCTrackInAcceptanceHist%s" %(trigger)) 
            if tracksMCKineWithClusters:
                triggerdata.AddTrackContainer("tracksMCKineWithClusters", TrackContainer(eventHist=deepcopy(eventhist), trackHist = tracksMCKineWithClusters))
            clusterhists = ["hClusterCalibHist","hClusterUncalibHist"]
            for clust in clusterhists:
                clhist = hlist.FindObject("%s%s" %(clust, trigger))
                if clhist:
                    tag = clust.replace("hCluster","").replace("Hist","")
                    #clhist.Sumw2()
                    triggerdata.AddClusterContainer(tag, ClusterContainer(eventHist = deepcopy(eventhist), clusterHist = clhist))
            result.SetData(trigger, triggerdata)
        return result
    
    def __ReadHistList(self):
        """
        Read the list of histograms from a given rootfile
        optionally the list can be wihtin a directory (i.e. when analysing lego train output)
        """
        result = {"spectra":None, "weights":None}
        inputfile = TFile.Open(self.__filename)
        if not inputfile or inputfile.IsZombie():
            raise self.FileReaderException(self.__filename)
        mydirectory = None
        path = self.__filename
        if self.__directory:
            path += "#%s" %(self.__directory)
            if not inputfile.cd(self.__directory):
                inputfile.Close()
                raise self.FileReaderException(path)
            else:
                mydirectory = gDirectory
        else:
            mydirectory = inputfile
            path += "#"
        rlist = mydirectory.Get("results")
        if self.__isReadWeights:
            result["weights"] = {"crosssection":rlist.FindObject("fHistXsection"), "trials":rlist.FindObject("fHistTrials")}
        hlist = rlist.FindObject("histosPtEMCalTriggerHistograms")
        inputfile.Close()
        if not hlist:
            raise self.FileReaderException("%s/histosPtEMCalTriggerHistograms" %(path))
        result["spectra"] = hlist
        return result
    
class LegoTrainFileReader(FileReader):
    """
    File reader adapted to the file format in the lego train
    """
    
    def __init__(self, filename, isMC = False):
        """
        Initialise file reader with filename and set the directory according to the definition in
        the lego train
        """
        FileReader.__init__(self, filename, isMC)
        self.SetDirectory("PtEMCalTriggerTask")
        
class ResultStructureReader(object):
    
    def __init__(self, filename):
        self.__filename = filename
        
    def ReadFile(self):
        return ResultData.BuildFromRootFile(self.__filename, "read")

def TestFileReader(filename):
    """
    Test procedure for the lego train file reader
    """
    testreader = LegoTrainFileReader(filename)
    return testreader.ReadFile()