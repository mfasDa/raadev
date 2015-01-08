'''
Created on Jan 8, 2015

@author: markus
'''

from base.struct.THnSparseWrapper import AxisFormat
from base.struct.THnSparseWrapper import THnSparseWrapper
from numpy import array as nparray

class AxisFormatJetTHnSparse(AxisFormat):
    
    def __init__(self):
        AxisFormat.__init__(self)
        self._axes["tracktpt"] = 0
        self._axes["jetpt"] = 1
        self._axes["tracketa"] = 2
        self._axes["trackphi"] = 3
        self._axes["vertexz"] = 4
        self._axes["mbtrigger"] = 5

class AxisFormatReducedJetTHnSparse(AxisFormat):
    
    def __init__(self):
        AxisFormat.__init__(self)
        self._axes["tracktpt"] = 0
        self._axes["tracketa"] = 1
        self._axes["trackphi"] = 2
        self._axes["vertexz"] = 3
        self._axes["mbtrigger"] = 4
        
class JetTHnSparseBase(THnSparseWrapper):
    
    def __init__(self, roothist):
        THnSparseWrapper.__init__(self, roothist)

    def SetEtaCut(self, etamin, etamax):
        self.ApplyCut("tracketa", etamin, etamax)
        
    def SetPhiCut(self, phimin, phimax):
        self.ApplyCut("trackphi", phimin, phimax)

    def SetVertexCut(self, vzmin, vzmax):
        self.ApplyCut("vertexz", vzmin, vzmax)
        
    def SetRequestSeenInMB(self, vzmin, vzmax):
        self.ApplyCut("mbtrigger", 1., 1.)

class JetTHnSparse(JetTHnSparseBase):
    '''
    classdocs
    '''

    def __init__(self, roothist):
        '''
        Constructor
        '''
        JetTHnSparseBase.__init__(self, roothist)
        self._axisdefinition = AxisFormatJetTHnSparse()
    
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
    
    def __init__(self, roothist):
        JetTHnSparseBase.__init__(self, roothist)
        self._axisdefinition = AxisFormatReducedJetTHnSparse()
    