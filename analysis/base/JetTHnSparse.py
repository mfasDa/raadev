'''
Created on Jan 8, 2015

@author: markus
'''

from base.THnSparseWrapper import AxisFormat,THnSparseWrapper
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

class JetTHnSparse(THnSparseWrapper):
    '''
    classdocs
    '''

    def __init__(self, roothist):
        '''
        Constructor
        '''
        THnSparseWrapper.__init__(self, roothist)
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
        result = self._rootthnsparse.Project(len(finaldims), finaldims)
        jetptstring= "jetpt%03d" %(minpt)
        result.SetName("%s%s" %(self._rootthnsparse.GetName(), jetptstring))
        #reset axis range
        self._rootthnsparse.GetAxis(self._axisdefinition.FindAxis("jetpt")).SetRange(currentlimits["min"], currentlimits["max"])
        self._CleanumProjection()
        return result