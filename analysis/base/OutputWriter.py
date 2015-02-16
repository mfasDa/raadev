'''
Created on 22.09.2014

@author: markusfasel
'''

from ROOT import TFile, TList, TObject
from __builtin__ import None

class OutputWriter:
    '''
    classdocs
    '''
    
    class OutputObject:
        
        def __init__(self, name):
            self.__name = name
            
        def GetName(self):
            return self.__name
        
        def Write(self):
            output = self.GetROOTPrimitive()
            output.Write(output.GetName(), TObject.kSingleKey)

        def __cmp__(self, other):
            if self.__name < other.GetName():
                return -1
            if self.__name > other.GetName():
                return 1
            return 0
            
    class NamedObject(OutputWriter.OutputObject):
        
        def __init__(self, name, rootobject):
            OutputWriter.OutputObject.__init__(self, name)
            self.__rootobject = rootobject
            
        def GetROOTPrimitive(self):
            self.__rootobject.SetName(self.__name)
            return self.__rootobject
        
        
    class ListObject(OutputWriter.OutputObject):
        
        def __init__(self, name):
            OutputWriter.OutputObject.__init__(self, name)
            self.__rootobjects = []
            
        def AddRootObject(self, name, rootobject):
            self.__rootobjects.append(OutputWriter.NamedObject(name, rootobject))
        
        def AddListObject(self, name):
            self.__rootobjects.append(OutputWriter.ListObject(name))
            
        def FindUpper(self, path):
            result = None
            for o in self.__rootobjects:
                if o.GetName() == path:
                    result = True
                    break
            return result
            
        def GetROOTPrimitive(self):
            output = TList()
            output.SetName(self.__name)
            for rootobject in self.__rootobjects:
                output.Add(rootobject.GetROOTPrimitive())
            return output


    def __init__(self, filename):
        '''
        Constructor
        '''
        self.__globalObjects = []
        self.__filename = filename
        
    def WriteOutput(self):
        output = TFile(self.__filename, "RECREATE")
        for entry in self._globalObjects:
            entry.Write()
        output.Close()
    
    def MakeList(self, listname, parent = None):
        if not parent:
            self.__globalObjects.append(OutputWriter.ListObject(listname))
        else:
            myparent = self.FindParent(parent)
            if myparent:
                parent.AddListObject(listname)
    
    def AddObject(self, name, rootobject, parent = None):
        if not parent:
            self.__globalObjects.append(OutputWriter.NamedObject(name, rootobject))
        else:
            myparent = self.FindParent(parent)
            if myparent:
                parent.AddRootObject(name, rootobject)
  
    def FindParent(self, parentname):
        result = None
        for o in self.__globalObjects:
            if o.GetName() == parentname:
                result = o
                break
            else:
                result = o.FindUpper(parentname)
            if result:
                break
        return result