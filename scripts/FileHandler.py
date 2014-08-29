#! /usr/bin/env python
"""
FileHandler.py
 Created on: 29.08.2014
     Author: markusfasel
"""

from ROOT import TFile,gDirectory
from SpectrumContainer import DataContainer

class ResultData:
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
    
    def __init__(self, name):
        """
        Initialise the result container
        """
        self.__name = name
        self.__data = {}
        
        # for iterator
        self.__currentIndex = 0
        
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
    
    def GetData(self, trigger):
        """
        Find data for a given trigger class by its name
        Raising a data exception if the trigger class is not avialable
        """
        if not self.__data.has_key(trigger):
            raise self.DataException(self.__name, trigger)
        return self.__data[trigger]
        
    def GetListOfTriggers(self):
        """
        Provide a list of trigger classes which are currently stored
        in the container
        """
        return self.__data.keys()
    
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
    
class FileReader:
    
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

    
    def __init__(self, filename):
        """
        Initialise file reader with name of the file to read
        """
        self.__filename = filename
        self.__directory = None
        
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
        hlist = self.__ReadHistList()
        if not hlist.GetEntries():
            raise self.FileReaderException("Empty list of histograms in file %s" %(self.__filename))
        result = ResultData("result")
        
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
            triggerdata = DataContainer(eventHist = eventhist, trackHist = trackhist)
            clusterhists = ["hClusterCalibHist","hClusterUncalibHist"]
            for clust in clusterhists:
                clhist = hlist.FindObject("%s%s" %(clust, trigger))
                if clhist:
                    tag = clust.replace("hCluster","").replace("Hist","")
                    triggerdata.AddClusterHist(clhist, tag)
            result.SetData(trigger, triggerdata)
        return result
    
    def __ReadHistList(self):
        """
        Read the list of histograms from a given rootfile
        optionally the list can be wihtin a directory (i.e. when analysing lego train output)
        """
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
        hlist = rlist.FindObject("histosPtEMCalTriggerHistograms")
        inputfile.Close()
        if not hlist:
            raise self.FileReaderException("%s/histosPtEMCalTriggerHistograms" %(path))
        return hlist
    
class LegoTrainFileReader(FileReader):
    """
    File reader adapted to the file format in the lego train
    """
    
    def __init__(self, filename):
        """
        Initialise file reader with filename and set the directory according to the definition in
        the lego train
        """
        FileReader.__init__(self, filename)
        self.SetDirectory("PtEMCalTriggerTask")

def TestFileReader(filename):
    """
    Test procedure for the lego train file reader
    """
    testreader = LegoTrainFileReader(filename)
    return testreader.ReadFile()