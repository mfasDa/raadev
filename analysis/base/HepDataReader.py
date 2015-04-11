'''
Created on Apr 10, 2015

@author: markus
'''

from base.DataCollection import DataCollection, Datapoint

class HepDataReader(object):
    '''
    classdocs
    '''


    def __init__(self, filename, dataname):
        '''
        Constructor
        '''
        self.__result = DataCollection(dataname)
        self.ReadFile(filename)
        
    def GetData(self):
        return self.__result        

    def ReadFile(self, filename):
        inputfile = open(filename)
        for line in inputfile:
            data = self.__ProcessDatapoint(line.replace("\n",""))
            if data:
                self.__result.AddDataPoint(data)
        inputfile.close()
        print "Successfully read in %d points" %(len(self.__result.GetPointList()))
        
    def __ProcessDatapoint(self, line):
        line = line.replace("E","e")
        tokens = line.split("\t")
        values = self.__RemoveEmpty(tokens)
        print values
        if not self.TestDigit(values[0]):
            print "%s is not a digit" %(values[0])
            return None
        result = Datapoint(float(values[0]), float(values[3]), float(values[0])-float(values[1]))
        result.AddErrorSource("stat", float(values[5]), float(values[4]))
        result.AddErrorSource("sys", float(values[7]), float(values[6]))
        result.Print()
        return result
    
    def TestDigit(self, value):
        try:
            test = float(value)
        except ValueError:
            return False
        return True
    
    def __RemoveEmpty(self, inputlist):
        output = []
        for entry in inputlist:
            if len(entry):
                output.append(entry)
        return output