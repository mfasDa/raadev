'''
Created on Jan 8, 2015

Representation of the track-based THnSparse

@author: markus
'''
from base.struct.THnSparseWrapper import THnSparseWrapper,AxisFormat
from copy import copy, deepcopy

class AxisFormatTracksOld(AxisFormat):
    '''
    Axis format for old track container
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
        AxisFormat.__init__(self, "tracksold")
        self._axes["pt"] = 0
        self._axes["eta"] = 1
        self._axes["phi"] = 2
        self._axes["vertexz"] = 3
        self._axes["pileup"] = 4
        self._axes["trackcuts"] = 5
        self._axes["MBtrigger"] = 6
        
    def __deepcopy__(self, other, memo):
        '''
        deep copy constructor
        '''
        newobj = AxisFormatTracksOld()
        newobj._Deepcopy(other, memo)
        return newobj
    
    def __copy__(self, other):
        '''
        shallow copy constructor
        '''
        newobj = AxisFormatTracksOld()
        newobj._Copy()
        return newobj
        
class AxisFormatTracksNew(AxisFormat):
    '''
    Axis format for new track container
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
        AxisFormat.__init__(self, "tracksnew")        
        self._axes["pt"] = 0
        self._axes["eta"] = 1
        self._axes["phi"] = 2
        self._axes["vertexz"] = 3
        self._axes["MBtrigger"] = 4
        
    def __deepcopy__(self, other, memo):
        '''
        deep copy constructor
        '''
        newobj = AxisFormatTracksNew()
        newobj._Deepcopy(other, memo)
        return newobj
    
    def __copy__(self, other):
        '''
        shallow copy constructor
        '''
        newobj = AxisFormatTracksNew()
        newobj._Copy()
        return newobj

class TrackTHnSparse(THnSparseWrapper):
    '''
    Base class for THnSparse in track format
    '''

    def __init__(self, roothist):
        '''
        Constructor
        '''
        THnSparseWrapper.__init__(self, roothist)
        
    def SetEtaCut(self, etamin, etamax):
        '''
        Apply cut in eta
        '''
        self.ApplyCut(self,etamin,etamax)
    
    def SetPhiCut(self, phimin, phimax):
        '''
        Apply cut in phi
        '''
        self.ApplyCut("phi", phimin, phimax)
    
    def SetVertexCut(self, vzmin, vzmax):
        '''
        Apply cut on vertex-z
        '''
        self.ApplyCut("vertexz", vzmin, vzmax)

    def SetRequestSeenInMB(self, vzmin, vzmax):
        '''
        Request that the track was also in a min. bias event
        '''
        self.ApplyCut("mbtrigger", 1., 1.)
        
class TrackTHnSparseOld(TrackTHnSparse):
    '''
    Class for old format track container
    '''
    
    def __init__(self, roothist):
        '''
        Constructor
        '''
        TrackTHnSparse.__init__(self, roothist)
        self._axisdefinition = AxisFormatTracksOld()

    def __deepcopy__(self, memo):
        '''
        Deep copy constructor
        '''
        result = TrackTHnSparseOld(deepcopy(self._rootthnsparse))
        result.CopyCuts(self._cutlist, True)
        return result
        
    def __copy__(self):
        '''
        Shallow copy constructor
        '''
        result = TrackTHnSparseOld(copy(self._rootthnsparse))
        result.CopyCuts(self._cutlist, False)
        return result

class TrackTHnSparseNew(TrackTHnSparse):
    '''
    Class for new format track container
    '''
    
    def __init__(self, roothist):
        '''
        Constructor
        '''
        TrackTHnSparse.__init__(self, roothist)
        self._axisdefinition = AxisFormatTracksNew()

    def __deepcopy__(self, memo):
        '''
        Deep copy constructor
        '''
        result = TrackTHnSparseNew(deepcopy(self._rootthnsparse))
        result.CopyCuts(self._cutlist, True)
        return result
        
    def __copy__(self):
        '''
        Shallow copy constructor
        '''
        result = TrackTHnSparseNew(copy(self._rootthnsparse))
        result.CopyCuts(self._cutlist, False)
        return result