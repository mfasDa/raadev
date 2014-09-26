"""
Created on 26.09.2014

Handler module for Monte-Carlo output from the ALICE Lego Trains. Lego train output
can be min. bias events or productions in pt-hat bins

@author: markusfasel
"""

from base.WeightHandler import WeightHandler
from base.FileHandler import LegoTrainFileReader

class MonteCarloDataCollection:
    """
    Collection of Monte-Carlo based outputs
    """

    def __init__(self, isPtHat = False):
        """
        Constructor
        """
        self.__weighthandler  = None
        if isPtHat:
            self.__weighthandler = WeightHandler
        self.__data = {"All":None}
        
    def AddData(self, results, pthatbin = -1,  weightdata = None):
        """
        Add new data (with or without pthat bins)
        """ 
        if pthatbin >= 0:
            self.__data[pthatbin] = results
            self.__weighthandler.AddPtHatBin(pthatbin, weightdata["crosssection"], weightdata["trials"])
        else:
            self.__data["All"] = results
            
    def GetData(self, pthatbin = -1):
        """
        Access to data (if necessary in a given pt-hat bin
        """
        if pthatbin >= 0:
            return self.__data[pthatbin]
        return self.__data["All"]
    
    def GetWeigthHandler(self):
        """
        Access to the weight handler
        """
        return self.__weighthandler
            
class MonteCarloFileHandler:
    """
    Class handling the reading of one file or a set of MonteCarlo files
    """
    
    def __init__(self):
        """
        Constructor
        """
        self.__datacollection = MonteCarloDataCollection()
        
    def GetCollection(self):
        """
        Access to the file collection
        """
        return self.__datacollection
    
    def AddFile(self, filename, pthatbin = -1):
        """
        Handle new file
        """
        reader = LegoTrainFileReader(filename, True)
        if pthatbin >= 0:
            reader.SetReadWeights() 
        self.__datacollection.AddData(reader.ReadFile(), pthatbin, reader.GetWeightHistograms())