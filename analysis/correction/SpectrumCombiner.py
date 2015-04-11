'''
Created on 22.09.2014

@author: markusfasel
'''

from copy import deepcopy
from base.TriggeredSpectrumScaler import TriggeredSpectrumScaler

class SpectrumCombiner(object):
    """
    Class combining the min. bias spectrum and the scaled-down triggered spectrum
    """

    def __init__(self, minbiasspectrum, triggeredspectrum):
        """
        Constructor
        """
        self.__minbiasspectrum = minbiasspectrum
        scaler = TriggeredSpectrumScaler(minbiasspectrum, triggeredspectrum)
        self.__triggeredspectrum = scaler.GetScaledTriggeredSpectrum()
        
    def MakeCombinedSpectrum(self, swappt):
        """
        Create a combined spectrum from the min bias spectrum and the triggered spectrum, using
        the points from the min bias spectrum up to a given pt, and the points from the triggered
        spectrum from that pt on
        """
        result = deepcopy(self.__minbiasspectrum)
        result.Sumw2()
        for mybin in range(1, result.GetXaxis().GetNbins()+1):
            inputspectrum = None
            if result.GetXaxis().GetBinUpEdge(mybin) <= swappt:
                inputspectrum = self.__minbiasspectrum
            else:
                inputspectrum = self.__triggeredspectrum
            result.SetBinContent(mybin, inputspectrum.GetBinContent(mybin))
            result.SetBinError(mybin, inputspectrum.GetBinError(mybin))
        return result