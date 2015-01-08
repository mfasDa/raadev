'''
Created on Jan 8, 2015

@author: markus
'''

from base.struct.THnSparseWrapper import THnSparseWrapper,AxisFormat
from copy import copy,deepcopy

class AxisFormatClustersOld(AxisFormat):
    '''
    Axis format for old cluster THnSparse
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
        AxisFormat.__init__(self, "clustersold")
        self._axes["energy"] = 0
        self._axes["vertexz"] = 1
        self._axes["pileup"] = 2
        self._axes["mbtrigger"] = 3
        
    def __deepcopy__(self, other, memo):
        '''
        Deep copy constructor
        '''
        newobj = AxisFormatClustersOld()
        newobj._Deepcopy(other, memo)
        return newobj
    
    def __copy__(self, other):
        '''
        Shallow copy constructor
        '''
        newobj = AxisFormatClustersOld()
        newobj._Copy()
        return newobj
    
class AxisFormatClustersNew(AxisFormat):
    '''
    Axis format for new cluster THnSparse
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
        AxisFormat.__init__(self, "clustersnew")
        self._axes["energy"] = 0
        self._axes["eta"] = 1
        self._axes["phi"] = 2
        self._axes["vertexz"] = 3
        self._axes["pileup"] = 4
        self._axes["mbtrigger"] = 5   
        
    def __deepcopy__(self, other, memo):
        '''
        Deep copy constructor
        '''
        newobj = AxisFormatClustersNew()
        newobj._Deepcopy(other, memo)
        return newobj
    
    def __copy__(self, other):
        '''
        Shallow copy constructor
        '''
        newobj = AxisFormatClustersNew()
        newobj._Copy()
        return newobj

class ClusterTHnSparse(THnSparseWrapper):
    '''
    Base class wrapper for cluster-based THnSparse
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
        
    def SetPileupRejection(self, on):
        if on and self._axisdefinition.FindAxis("pileup"):
            self.ApplyCut("pileup", 1., 1.)
    
class ClusterTHnSparseOld(THnSparseWrapper):
    '''
    Old format cluster THnSparse
    '''
    
    def __init__(self, roothist):
        '''
        Constructor
        '''
        ClusterTHnSparse.__init__(self, roothist)
        self._axisdefinition = AxisFormatClustersOld()
        
    def __deepcopy__(self, memo):
        '''
        Deep copy constructor
        '''
        result = ClusterTHnSparseOld(deepcopy(self._rootthnsparse))
        result.CopyCuts(self._cutlist, True)
        return result
        
    def __copy__(self):
        '''
        Shallow copy constructor
        '''
        result = ClusterTHnSparseOld(copy(self._rootthnsparse))
        result.CopyCuts(self._cutlist, False)
        return result

class ClusterTHnSparseNew(THnSparseWrapper):
    '''
    New format cluster THnSparse
    '''
    
    def __init__(self, roothist):
        '''
        Constructor
        '''
        ClusterTHnSparse.__init__(self, roothist)
        self._axisdefinition = AxisFormatClustersNew()

    def __deepcopy__(self, memo):
        '''
        Deep copy constructor
        '''
        result = ClusterTHnSparseNew(deepcopy(self._rootthnsparse))
        result.CopyCuts(self._cutlist, True)
        return result
        
    def __copy__(self):
        '''
        Shallow copy constructor
        '''
        result = ClusterTHnSparseNew(copy(self._rootthnsparse))
        result.CopyCuts(self._cutlist, False)
        return result