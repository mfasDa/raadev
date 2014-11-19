#! /usr/bin/env python
"""
FileHandler.py
 Created on: 29.08.2014
     Author: markusfasel
"""

from ROOT import TFile,TIter,TObject,gDirectory,gROOT
from copy import copy, deepcopy
from SpectrumContainer import DataSet, ClusterContainer, TrackContainer, SpectrumContainer, MergeException

class ResultData(object):
    """
    Container for the result data
    Keeps the data containers for different trigger classes
    Access is implemented by the trigger class name
    """
    
    class DataException(Exception):
        """
        Exception handling for the result data
        """
        
        def __init__(self, containerName, trigger):
            """
            Initialise exception with the container name which raised the exception
            and a trigger which is not found
            """
            self.__containerName = containerName
            self.__trigger = trigger
            
        def __str__(self):
            """
            Create error message
            """
            return "Data for trigger class %s not found in container %s" %(self.__trigger, self.__containerName)
        
        def SetTrigger(self, trigger):
            """
            Set trigger name
            """
            self.__trigger = trigger
            
        def GetTrigger(self):
            """
            Access trigger name
            """
            return self.__trigger
        
        def SetContainerName(self, containerName):
            """
            Set container name
            """
            self.__containerName = containerName
            
        def GetContainerName(self):
            """
            Access container name
            """
            return self.__containerName
        
        Trigger = property(GetTrigger, SetTrigger)
        ContainerName = property(GetContainerName, SetContainerName)
    
    def __init__(self, name):
        """
        Initialise the result container
        """
        self.__name = name
        self.__data = {}
        self.__mctruth = None
        
        # for iterator
        self.__currentIndex = 0
        
    def __copy__(self):
        """
        Shallow copy constructor
        """
        print "Simple copy called from %s" %(self.__class__)
        newobject = ResultData(self.Name)
        if self.__mctruth:
            newobject.MCTruth = copy(self.__mctruth)
        for trigger in self.__data.keys():
            newobject.SetData(trigger, copy(self.__data[trigger]))
        return newobject
     
    def __deepcopy__(self, memo):
        """
        Deep copy constructor
        """
        print "deep copy called from %s" %(self.__class__)
        newobject = ResultData(self.Name)
        if self.__mctruth:
            newobject.MCTruth = deepcopy(self.__mctruth, memo)
        for trigger in self.__data.keys():
            newobject.SetData(trigger, deepcopy(self.__data[trigger], memo))
        return newobject
        
    def SetName(self, name):
        """
        Change name of the result container
        """
        self.__name = name
        
    def SetData(self, trigger, data):
        """
        Add a new trigger class with the corresponding data to the result
        container
        """
        self.__data[trigger] = data
        
    def GetName(self):
        """
        Access name of the trigger class
        """
        return self.__name
    
    def SetMCTruth(self, MCtrueSpectrum):
        """
        Set the MC truth to the result data
        """
        self.__mctruth = MCtrueSpectrum
        
    def GetMCTruth(self):
        """
        Access MC truth from the result data
        """
        return self.__mctruth
    
    def GetData(self, trigger):
        """
        Find data for a given trigger class by its name
        Raising a data exception if the trigger class is not avialable
        """
        if not self.__data.has_key(trigger):
            raise self.DataException(self.__name, trigger)
        return self.__data[trigger]
    
    # Properies
    Name = property(GetName, SetName)
    MCTruth = property(GetMCTruth, SetMCTruth)
    
    def Add(self, other):
        """
        Add MCTruth and datasets from other data to this MCTruth and the corresponding data set
        """
        if not isinstance(other, ResultData):
            raise MergeException("Type incompatibility: this(ResultData), other(%s)" %(str(other.__class__)))
        nfailure =0
        for trigger in self.GetListOfTriggers():
            if other.HasTrigger(trigger):
                self.__data[trigger].Add(other.GetData(trigger))
            else:
                nfailure += 1
        if self.__mctruth:
            self.__mctruth.Add(other.MCTruth)
        if nfailure > 0:
            raise MergeException("Unmerged histograms in this data")
    
    def Scale(self, scalefactor):
        """
        Scale all datasets and the MC truth by the scalefactor
        """
        for triggerdata in self.__data.values():
            triggerdata.Scale(scalefactor)
        # Scale also the MC truth
        self.__mctruth.Scale(scalefactor)
        
    def Write(self, rootfilename):
        """
        Write Structure to file
        """
        writer = TFile(rootfilename, "Recreate")
        writer.cd()
        for triggername, triggerdata in self.__data.iteritems():
            rootprim = triggerdata.GetRootPrimitive(triggername)
            rootprim.Write(triggername, TObject.kSingleKey)
        if self.__mctruth:
            self.__mctruth.GetRootPrimitive().Write("MCTruth", TObject.kSingleKey)
        writer.Close() 
        
    @staticmethod
    def BuildFromRootFile(filename, name):
        result = ResultData(name)
        inputfile = TFile.Open(filename)
        gROOT.cd()
        keyIter = TIter(inputfile.GetListOfKeys())
        key = keyIter.Next()
        while key:
            if key.GetName() == "MCTruth":
                result.SetMCTruth(SpectrumContainer.BuildFromRootPrimitive(key.ReadObj()))
            else:
                result.SetData(key.GetName(), DataSet.BuildFromRootPrimitive(key.ReadObj()))
            key = keyIter.Next()
        inputfile.Close()
        print "Results successfully reconstructed from file %s" %(filename)
        #result.Print()
        return result
    
    def Print(self):
        """
        Print status of the result data sets
        """
        print "Content of result data:"
        for trg, data in self.__data.items():
            print "Trigger %s" %(trg)
            data.Print()
        
    def GetListOfTriggers(self):
        """
        Provide a list of trigger classes which are currently stored
        in the container
        """
        return self.__data.keys()
    
    def HasTrigger(self, triggername):
        """
        Check if the container has a given trigger type
        """
        return triggername in self.__data.keys()
    
    def __iter__(self):
        """
        Initialise the iterator
        """
        self.__curentIndex = 0
        return self
    
    def next(self):
        """ 
        Iterate over trigger classes
        The iterator always returns a tuple of triggerclass and data
        """
        if self.__currentIndex < len(self.__data.keys()):
            result = self.__data.keys()[self.__currentIndex], self.__data[self.__data.keys()[self.__currentIndex]]
            self.__currentIndex += 1
            return result
        else:
            raise StopIteration
    
    def __len__(self):
        """
        Return the amount of trigger classes
        """
        return len(self.__data)
    
    def __getItem__(self, key):
        """
        Access trigger item by the [] operator
        """
        return self.GetData(key)
    
    def __contains__(self, item):
        return item in self.__data.keys()
    
class ResultDataBuilder(object):
    """
    General data structure builder interfacing different input file formats
    """
    
    def __init__(self, filetype, filename):
        """
        Constructor
        """
        reader = None
        if filetype == "lego":
            reader = LegoTrainFileReader(filename)
        elif filetype == "resultfile":
            reader = ResultStructureReader(filename)
        self.__results = None
        if reader:
            self.__results = reader.ReadFile()
            
    def GetResults(self):
        """
        Access to data
        """
        return self.__results
    
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
                triggerdata.AddTrackContainer("tracksMCKine", TrackContainer(eventHist=deepcopy(eventhist)), trackHist = tracksMCKine)
            tracksMCKineWithClusters = hlist.FindObject("hMCTrackInAcceptanceHist%s" %(trigger)) 
            if tracksMCKineWithClusters:
                triggerdata.AddTrackContainer("tracksMCKineWithClusters", TrackContainer(eventHist=deepcopy(eventhist)), trackHist = tracksMCKineWithClusters)
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