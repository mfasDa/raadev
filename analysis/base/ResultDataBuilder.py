'''
Created on Jan 5, 2015

@author: markus
'''

from FileHandler import LegoTrainFileReader, ResultStructureReader

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
