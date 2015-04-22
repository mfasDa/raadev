#**************************************************************************
#* Copyright(c) 1998-2014, ALICE Experiment at CERN, All rights reserved. *
#*                                                                        *
#* Author: The ALICE Off-line Project.                                    *
#* Contributors are mentioned in the code where appropriate.              *
#*                                                                        *
#* Permission to use, copy, modify and distribute this software and its   *
#* documentation strictly for non-commercial purposes is hereby granted   *
#* without fee, provided that the above copyright notice appears in all   *
#* copies and that both the copyright notice and this permission notice   *
#* appear in the supporting documentation. The authors make no claims     *
#* about the suitability of this software for any purpose. It is          *
#* provided "as is" without express or implied warranty.                  *
#**************************************************************************
'''
Wrapper class for THnSparse with EMCAL cluster information
Interfaces are available for the old and new format

:organization: ALICE Collaboration
:copyright: 1998-2014, ALICE Experiment at CERN, All rights reserved.

:author: Markus Fasel
:contact: markus.fasel@cern.ch
:organization: Lawrence Berkeley National Laboratory
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
        self._axes["mbtrigger"] = 4  
        
    def __deepcopy__(self, memo):
        '''
        Deep copy constructor
        '''
        newobj = AxisFormatClustersNew()
        newobj._Deepcopy(self, memo)
        return newobj
    
    def __copy__(self, other):
        '''
        Shallow copy constructor
        '''
        newobj = AxisFormatClustersNew()
        newobj._Copy(self)
        return newobj

class ClusterTHnSparse(THnSparseWrapper):
    '''
    Base class wrapper for cluster-based THnSparse
    '''
    
    def __init__(self, roothist):
        '''
        Constructor
        
        :param roothist: underlying root THnSparse
        :type roothist: THnSparse
        '''
        THnSparseWrapper.__init__(self, roothist) 
                                  
    def SetEtaCut(self, etamin, etamax):
        '''
        Apply cut in eta
        
        :param etamin: min. eta cut
        :type etamin: float
        :param etamax: max. eta cut
        :type etamax: float
        '''
        self.ApplyCut("eta",etamin,etamax)
    
    def SetPhiCut(self, phimin, phimax):
        '''
        Apply cut in phi
        
        :param phimin: min. phi cut
        :type phimin: float
        :param phimax: max. phi cut
        :type phimax: float
        '''
        self.ApplyCut("phi", phimin, phimax)
    
    def SetVertexCut(self, vzmin, vzmax):
        '''
        Apply cut on vertex-z

        :param vzmin: min. vertex-z cut
        :type vzmin: float
        :param vzmax: max. vertex-z cut
        :type vzmax: float
        '''
        self.ApplyCut("vertexz", vzmin, vzmax)

    def SetRequestSeenInMB(self):
        '''
        Request that the track was also in a min. bias event
        '''
        self.ApplyCut("mbtrigger", 1., 1.)
        
    def SetPileupRejection(self, on):
        """
        Set Pileup rejection cut
        
        :param on: if true, pileup rejection is applied (only old format)
        :type on: bool
        """
        if on and self._axisdefinition.FindAxis("pileup"):
            self.ApplyCut("pileup", 1., 1.)
            
    def Print(self):
        pass
    
class ClusterTHnSparseOld(ClusterTHnSparse):
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

class ClusterTHnSparseNew(ClusterTHnSparse):
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