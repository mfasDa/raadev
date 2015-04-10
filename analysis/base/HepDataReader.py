'''
Created on Apr 10, 2015

@author: markus
'''

from base.DataCollection import DataCollection, Datapoint

class HepDataReader(object):
    '''
    classdocs
    '''


    def __init__(self, filename):
        '''
        Constructor
        '''
        self.__result = DataCollection()
        self.ReadFile(filename)
        
    def GetData(self):
        return self.__data()
        
    def ReadFile(self, filename):
        inputfile = open(filename)
        for line in inputfile:
            data = self.__ProcessDatapoint(line)
            if data:
                self.__result.AddDataPoint(data)
        inputfile.close()
        
    def __ProcessDatapoint(self, line):
        tokens = line.split(" ")
        values = self.__RemoveEmpty(tokens)
        if not values[0].isdigit():
            return None
        result = Datapoint(values[0], values[3], values[0]-values[1])
        result.AddErrorSource("stat", values[5], values[4])
        result.AddErrorSource("sys", values[7], values[6])
        return result
    
    def __RemoveEmpty(self, inputlist):
        output = []
        for entry in inputlist:
            if len(entry):
                output.append(entry)
        return output