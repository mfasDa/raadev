'''
Created on Jan 8, 2015

Representation of a jet-based THnSparse

@author: markus
'''

from base.struct.THnSparseWrapper import AxisFormat
from base.struct.THnSparseWrapper import THnSparseWrapper
from copy import copy, deepcopy
from numpy import array as nparray

class AxisFormatJetTHnSparse(AxisFormat):
    '''
    Axis format for jet-based track THnSparse
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
        AxisFormat.__init__(self, "jets")
        self._axes["tracktpt"] = 0
        self._axes["jetpt"] = 1
        self._axes["tracketa"] = 2
        self._axes["trackphi"] = 3
        self._axes["vertexz"] = 4
        self._axes["mbtrigger"] = 5    
    
    def __deepcopy__(self, other, memo):
        '''
        Deep copy constructor
        '''
        newobj = AxisFormatJetTHnSparse()
        newobj._Deepcopy(other, memo)
        return newobj
    
    def __copy__(self, other):
        '''
        Shallow copy constructor
        '''
        newobj = AxisFormatJetTHnSparse()
        newobj._Copy()
        return newobj

class AxisFormatReducedJetTHnSparse(AxisFormat):
    '''
    Axis format for projected THnSparse
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
        AxisFormat.__init__(self, "jetsreduced")
        self._axes["tracktpt"] = 0
        self._axes["tracketa"] = 1
        self._axes["trackphi"] = 2
        self._axes["vertexz"] = 3
        self._axes["mbtrigger"] = 4

    def __deepcopy__(self, other, memo):
        '''
        Deep copy constructor
        '''
        newobj = AxisFormatReducedJetTHnSparse()
        newobj._Deepcopy(other, memo)
        return newobj
    
    def __copy__(self, other):
        '''
        Shallow copy constructor
        '''
        newobj = AxisFormatReducedJetTHnSparse()
        newobj._Copy()
        return newobj
        
class JetTHnSparseBase(THnSparseWrapper):
    '''
    Base class for Jet THnSparses
    Can not be used directly, but classes must inherit from it
    '''
    
    def __init__(self, roothist):
        '''
        Constructor
        '''
        THnSparseWrapper.__init__(self, roothist)

    def SetEtaCut(self, etamin, etamax):
        '''
        Apply eta cut
        '''
        self.ApplyCut("tracketa", etamin, etamax)
        
    def SetPhiCut(self, phimin, phimax):
        '''
        Apply phi cut
        '''
        self.ApplyCut("trackphi", phimin, phimax)

    def SetVertexCut(self, vzmin, vzmax):
        '''
        Apply cut on the position of the z-vertex
        '''
        self.ApplyCut("vertexz", vzmin, vzmax)
        
    def SetRequestSeenInMB(self, vzmin, vzmax):
        '''
        Request that the track was also in a min. bias event
        '''
        self.ApplyCut("mbtrigger", 1., 1.)

class JetTHnSparse(JetTHnSparseBase):
    '''
    THnSparse with information for Tracks in jets
    '''

    def __init__(self, roothist):
        '''
        Constructor
        '''
        JetTHnSparseBase.__init__(self, roothist)
        self._axisdefinition = AxisFormatJetTHnSparse()

    def __deepcopy__(self, memo):
        '''
        Deep copy constructor
        '''
        result = JetTHnSparse(deepcopy(self._rootthnsparse))
        result.CopyCuts(self._cutlist, True)
        return result
        
    def __copy__(self):
        '''
        Shallow copy constructor
        '''
        result = JetTHnSparse(copy(self._rootthnsparse))
        result.CopyCuts(self._cutlist, False)
        return result
    
    def MakeProjectionMinJetPt(self, minpt):
        '''
        Reduce THnSparse restricted to track axis, selecting tracks from jets with given
        minimum jet pt
        '''
        self._PrepareProjection()
        finaldims = nparray([\
                             self._axisdefinition.FindAxis("trackpt"),\
                             self._axisdefinition.FindAxis("tracketa"),\
                             self._axisdefinition.FindAxis("trackphi"),\
                             self._axisdefinition.FindAxis("vertexz"),\
                             self._axisdefinition.FindAxis("mbtrigger"),\
                            ])
        currentlimits = {\
                         "min":self._rootthnsparse.GetAxis(self._axisdefinition.FindAxis("jetpt")).GetFirst(),\
                         "max":self._rootthnsparse.GetAxis(self._axisdefinition.FindAxis("jetpt")).GetLast()\
        }
        newlimits = {\
                     "min":self._rootthnsparse.GetAxis(self._axisdefinition.FindAxis("jetpt")).FindBin(minpt),\
                     "max":currentlimits["max"],\
                     }
        # Make cut in jet pt
        self._rootthnsparse.GetAxis(self._axisdefinition.FindAxis("jetpt")).SetRange(newlimits["min"], newlimits["max"])
        # create projected Matrix
        result = self._rootthnsparse.Projection(len(finaldims), finaldims)
        jetptstring= "jetpt%03d" %(minpt)
        result.SetName("%s%s" %(self._rootthnsparse.GetName(), jetptstring))
        #reset axis range
        self._rootthnsparse.GetAxis(self._axisdefinition.FindAxis("jetpt")).SetRange(currentlimits["min"], currentlimits["max"])
        self._CleanumProjection()
        return result
    
    
class ReducedJetTHnSparse(JetTHnSparseBase):
    '''
    Class for Jet THnSparse after projecting for different minimum jet pts
    '''
    
    def __init__(self, roothist):
        '''
        Constructor
        '''
        JetTHnSparseBase.__init__(self, roothist)
        self._axisdefinition = AxisFormatReducedJetTHnSparse()

    def __deepcopy__(self, memo):
        '''
        Deep copy constructor
        '''
        result = ReducedJetTHnSparse(deepcopy(self._rootthnsparse))
        result.CopyCuts(self._cutlist, True)
        return result
        
    def __copy__(self):
        '''
        Shallow copy constructor
        '''
        result = ReducedJetTHnSparse(copy(self._rootthnsparse))
        result.CopyCuts(self._cutlist, False)
        return result
    