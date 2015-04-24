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
Module for control plots created during the correction procedure

:organization: ALICE Collaboration
:copyright: 1998-2015, ALICE Experiment at CERN, All rights reserved.

:author: Markus Fasel
:contact: markus.fasel@cern.ch
:organization: Lawrence Berkeley National Laboratory
"""

from base.Graphics import TwoPanelPlot, Frame, GraphicsObject, Style
from base.FrameTemplates import NormalizedPtSpectrumFrame, EfficiencyFrame
from base.Helper import MakeRatio
from copy import deepcopy
from ROOT import kBlack, kBlue, kRed

class EfficiencyCorrectionPlot(TwoPanelPlot):
    """
    Comparison plot before/after efficiency correction
    """

    def __init__(self, rawspectrum, correctedspectrum):
        """
        Constructor
        
        :param rawspectrum: Raw spectrum, before efficiency correction
        :type rawspectrum: TH1
        :param rawspectrum: efficiency corrected spectrum, after efficiency correction
        :type correctedspectrum: TH1
        """
        TwoPanelPlot.__init__(self)
        self.__rawspectrum = deepcopy(rawspectrum)
        self.__correctedspectrum = correctedspectrum
        self.Create()
        
    def Create(self):
        """
        Create the plot
        """
        self._CreateCanvas("EffCorrectionControl", "Comparison before/after efficiency correction")
    
        specpad = self._OpenPad(0)
        specpad.GetPad().SetLogy()
        specpad.DrawFrame(NormalizedPtSpectrumFrame("specframe"))
        specpad.DrawGraphicsObject(GraphicsObject(self.__rawspectrum, Style(kBlack, 24)), addToLegend = True, title = "Before correction")
        specpad.DrawGraphicsObject(GraphicsObject(self.__correctedspectrum, Style(kBlue, 25)), addToLegend = True, title = "After correction")
        specpad.CreateLegend(0.55, 0.75, 0.89, 0.89)
    
        ratpad = self._OpenPad(1)
        ratframe = Frame("ratframe", 0., 100., 0., 2.)
        ratframe.SetXtitle("p_{t} (GeV/c)")
        ratframe.SetYtitle("After / Before correction")
        ratpad.DrawFrame(ratframe)
        ratpad.DrawGraphicsObject(GraphicsObject(MakeRatio(self.__afterCorrection, self.__beforeCorrection), Style(kBlack, 20)))
        
class EfficienyFitPlot(TwoPanelPlot):
    """
    Control plot for efficency over fit
    """
    
    def __init__(self, data, param):
        """
        Constructor
        
        :param data: evaluated efficiency
        :type data: TH1
        :param param: fit to the efficiency
        :type param: TF1
        """
        TwoPanelPlot.__init__(self)
        self.__data = deepcopy(data)
        self.__param = deepcopy(param)
        self.Create()
    
    def __MakeDataOverFit(self, data, model):
        """
        Calculate ratio efficiency/param
        
        :param data: efficiency
        :type data: TH1
        :param model: efficiency model
        :type model: TF1
        """
        result = deepcopy(data)
        result.SetName("DataOverFit")
        for i in range(1, data.GetXaxis().GetNbins()):
            pval = model.Eval(result.GetXaxis().GetBinCenter(i))
            result.SetBinContent(i, result.GetBinContent(i)/pval)
            result.SetBinError(i, result.GetBinError(i)/pval)
        return result
    
    def Create(self):
        """
        Create the plot
        """
        self._CreateCanvas("EffFitComparison", "Comparison of Efficiency vs, Fit")
    
        effpad = self._OpenPad(0)
        effframe = Frame("effframe", 0., 100., 0., 1.2)
        effframe.SetXtitle("p_{t, gen} (GeV/c)")
        effframe.SetYtitle("Efficiency")
        effpad.DrawFrame(EfficiencyFrame("efficiency"))
        effpad.DrawGraphicsObject(GraphicsObject(self.__data, Style(kBlack, 24)), addToLegend = True, title = "Efficiency")
        effpad.DrawGraphicsObject(GraphicsObject(self.__param, Style(kRed, 25)), addToLegend = True, title = "Param", option="l")
        effpad.CreateLegend(0.65, 0.75, 0.89, 0.89)
    
        ratpad = self._OpenPad(1)
        ratframe = Frame("ratframe", 0., 100., 0.5, 1.5)
        ratframe.SetXtitle("p_{t, gen} (GeV/c)")
        ratframe.SetYtitle("Data  / Fit")
        ratpad.DrawFrame(ratframe)
        ratpad.DrawGraphicsObject(GraphicsObject(self.__MakeDataOverFit(self.__data, self.__param), Style(kBlack, 20)))