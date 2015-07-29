#**************************************************************************
#* Copyright(c) 1998-2015, ALICE Experiment at CERN, All rights reserved. *
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
"""
Modules with necessary tools for the efficiency corection
- Efficiency correction
- Normalization
Corrections are done in 1D

:organization: ALICE Collaboration
:copyright: 1998-2015, ALICE Experiment at CERN, All rights reserved.

:author: Markus Fasel
:contact: markus.fasel@cern.ch
:organization: Lawrence Berkeley National Laboratory
"""

from math import pi
from copy import deepcopy
from ROOT import TF1

from correction.EfficiencyCorrectionQAPlots import EfficiencyCorrectionPlot, EfficienyFitPlot

class CorrectionQA(object):
    """
    Container data for correction QA plots
    """
    
    def __init__(self):
        """
        Constructor
        """
        self.__qaplots = {}
        
    def AddQAPlot(self, name, plot):
        """
        Add new QA plot
        
        :param name: Name of the QA plot
        :type name: str
        :param plot: Plot to be added
        :type plot: PlotBase
        """
        self.__qaplots[name] = plot
        
    def FindQAPlot(self, name):
        """
        Find QA plot in the set of QA plots
        
        :param name: Name of the plot
        :type name: str
        :return: the QA plot
        :rtype: PlotBase
        """
        return self.__qaplots[name]
    
    def GetQAPlots(self):
        """
        Get the dictionary of QA Plots
        
        :return: QA plots
        :rtype: dictionary
        """
        return self.__qaplots
    
class EfficiencyCorrection(object):
    """
    Base class for efficiency corrections
    """
    
    def __init__(self, rawspectrum, rawefficiency):
        """
        Constructor, initializing raw spectrum and efficiency
        
        :param rawspectrum: The raw spectrum to be corrected
        :type rawspectrum: TH1
        :param rawefficiency: Efficiency used for the correction
        :type raweffficiency: TH1
        """
        self._rawspectrum = rawspectrum
        self._rawefficiency = rawefficiency
        self._resolutionCorrection = None
        self._correctionQA = CorrectionQA()
    
    def SetResolutionCorrection(self, resolutionCorrection):
        """
        Set the resolution correction
        
        :param resolutionCorrection: pt-resolution correction
        :type resolutionCorrection: TF1
        """
        self._resolutionCorrection = resolutionCorrection
    
    def GetCorrectedSpectrum(self):
        """
        Make the corrected spectrum: delegate efficiency correction to the protected methods ApplyCorrection in the inheriting
        classes. Itself performs only resolution correction
        
        :return: The efficiency and resolution corrected spectrum
        :rtype: TH1
        """
        correctedspectrum = self._ApplyCorrection()
        if self._resolutionCorrection:
            # Apply also resolution correction
            for mybin in range(1, correctedspectrum.GetXaxis().GetNbins()+1):
                bincenter = correctedspectrum.GetXaxis().GetBinCenter(mybin) 
                correctionfactor = self._resolutionCorrection.Eval(bincenter)
                correctedspectrum.SetBinContent(mybin, correctedspectrum.GetBinContent(mybin)*correctionfactor)
                correctedspectrum.SetBinError(mybin, correctedspectrum.GetBinError(mybin)*correctionfactor)
        self._correctionQA.AddQAPlot("EfficiencyCorrection", EfficiencyCorrectionPlot(self._rawspectrum, correctedspectrum))
        return correctedspectrum
    
    def GetQAPlots(self):
        """
        Get the list of QAPlots
        
        :return: The QA Plot holder
        :rtype: CorrectionQA
        """
        return self._correctionQA
    
    def FindQAPlot(self, name):
        """
        Find a QA plot among the list of QA plots
        
        :param name: Name of the plot
        :type name: str
        :return: the QA plot
        :rtype: PlotBase
        """
        return self._correctionQA.FindQAPlot(name)
    
class EfficiencyCorrectionBinByBin(EfficiencyCorrection):
    """
    Simple bin-by-bin correction method
    """
    
    def __init__(self, rawspectum, rawefficiency):
        """
        Constructor, initializing raw spectrum and efficiency
        
        :param rawspectrum: The raw spectrum to be corrected
        :type rawspectrum: TH1
        :param rawefficiency: Efficiency used for the correction
        :type raweffficiency: TH1
        """
        EfficiencyCorrection.__init__(self, rawspectum, rawefficiency)

    def _ApplyCorrection(self):
        """
        Apply efficiency correction
        """
        result = deepcopy(self.__rawspectrum)
        result.Divide(self.__rawspectrum, self.__efficiency, 1., 1., 'b')
        return result
  
class EfficiencyCorrectionModel(EfficiencyCorrection):
    
    def __init__(self, rawspectum, rawefficiency, model = "pol1"):
        """
        Constructor, initializing raw spectrum and efficiency
        
        :param rawspectrum: The raw spectrum to be corrected
        :type rawspectrum: TH1
        :param rawefficiency: Efficiency used for the correction
        :type raweffficiency: TH1
        :param model: Efficiency model
        :type model: str
        """
        EfficiencyCorrection.__init__(self, rawspectum, rawefficiency)
        self._model = model
        self._fits = {}
        
    def __MakeEfficencyFit(self):
        """
        Make fit of the efficiency with the given parameterization
        For error estimation also move up or down the points by their errors
        """
        self._fits["center"] = self.__FitEfficiency(self._rawefficiency)
        self._correctionQA.AddQAPlot("FitQA", EfficienyFitPlot(self._rawefficiency, self._fits["center"]))

        # Move all points up by their uncertainty
        def GetMovedPoints(inputspectrum, isUpper):
            """
            Local helper function moving all points by their errors
            
            :param inputspectrum: Input spectrum
            :type inputspectrum: TH1
            :param isUpper: If true, points will be move up, otherwise down
            :type isUpper: bool
            """
            result = deepcopy(inputspectrum)
            for point in range(1, result.GetXaxis().GetNbins()+1):
                value = result.GetBinContent(point) 
                error = result.GetBinError(point)
                result.SetBinContent(point, value + error if isUpper else value - error)
            return result

        spectrumlow = GetMovedPoints(self._rawefficiency, False)
        self._fits["lower"] = self.__FitEfficiency(spectrumlow)
        spectrumhigh = GetMovedPoints(self._rawefficiency, True)
        self._fits["upper"] = self.__FitEfficiency(spectrumhigh)
        
    def __FitEfficiency(self, inputvalues):
        """
        Fit efficiency by a given model
        """
        result = TF1("efficiencyModel", self.__model, 0., 100.)
        inputvalues.Fit(result, "N", "", 10, 70)
        return result

    def _ApplyCorrection(self):
        """
        Apply efficiency correction
        """
        self.__MakeEfficencyFit()
        result = deepcopy(self.__rawspectrum)
        for ibin in range(1, result.GetXaxis().GetNbins() +1):
            bcent = result.GetXaxis().GetBinCenter(ibin)
            effval = self._fits["center"].Eval(bcent)
            y  = result.GetBinContent(ibin)/effval
            
            # apply error propagation
            # divide upper value by lower efficiency and vice versa
            efflow = self._fits["lower"].Eval(bcent)
            effhigh = self._fits["upper"].Eval(bcent)
            ehigh = (result.GetBinContent(ibin) + result.GetBinError(ibin))/efflow - y 
            elow = y - (result.GetBinContent(ibin) - result.GetBinError(ibin))/effhigh
            result.SetBinContent(ibin, y)
            result.SetBinError(ibin, max(ehigh, elow))
        return result


class Normalizer(object):
    """
    Tool normalizing a fully corrected spectrum
    """

    def __init__(self, efficiencyCorrected):
        """
        Constructor
        
        :param efficiencyCorrected: efficiency corrected spectrum
        :type efficiencyCorrected: TH1
        """
        self.__correctedspectrum = efficiencyCorrected
        self.__etarange = {"min":-0.8, "max":0.8}
        
    def SetEtaRange(self, etamin, etamax):
        """
        Set the eta range
        
        :param etamin: min eta
        :type etamin: float
        :param etamax: max eta
        :type etamax: float
        """
        self.__etarange["min"] = etamin
        self.__etarange["max"] = etamax
    
    def GetNormalized(self):
        """
        Make the normalized spectrum
        
        :return: the normalized spectrum
        :rtype: TH1
        """
        deta = abs(self.__etarange["max"] - self.__etarange["min"])
        result = deepcopy(self.__efficiencyCorrected)
        for ib in range(1, self.__efficiencyCorrected.GetXaxis().GetNbins()+1):
            factor = 1/(2*pi*self.__efficiencyCorrected.GetXaxis().GetBinCenter(ib)*deta)
            result.SetBinContent(ib, result.GetBinContent(ib)*factor)
            result.SetBinError(ib, result.GetBinError(ib)*factor)
        return result