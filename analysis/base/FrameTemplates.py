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
"""
Helper module with pre-defined frames 

:organization: ALICE Collaboration
:copyright: 1998-2014, ALICE Experiment at CERN, All rights reserved

:author: Markus Fasel , 
:contact: <markus.fasel@cern.ch>
:organization: Lawrence Berkeley National Laboratory
"""
from base.Graphics import Frame

class NormalizedPtSpectrumFrame(Frame):
    """
    Frame definition for fully normalized p-t spectrum
    """

    def __init__(self, name):
        """
        Constructor

        :param name: Name of the frame
        :type name: str
        """
        Frame.__init__(self, name, 0., 100., 1e-12, 10)
        self.SetXtitle("p_{t} (GeV/c)")
        self.SetYtitle("1/(2 #pi p_{t} N_{ev}) dN/(dp_{t} d#eta) (GeV/c)^{-2}")
        
class RawSpectrumFrame(Frame):
    """
    Frame class for event and bin-width normalized raw spectrum plots
    """
    
    def __init__(self, name):
        """ 
        Constructor

        :param name: Name of the frame
        :type name: str
        """
        Frame.__init__(self, name, 0., 100., 1e-12, 100.)
        self.SetXtitle("p_{t} (GeV/c)")
        self.SetYtitle("1/N_{ev} dN/dp_{t} ((GeV/c)^{-1})")
        
class EfficiencyFrame(Frame):
    """
    Frame definition for Efficiency plots
    """
    
    def __init__(self, name):
        """
        Constructor

        :param name: Name of the frame
        :type name: str
        """
        Frame.__init__(self, name, 0., 100., 0., 1.)
        self.SetXtitle("p_{t, gen} (GeV/c)")
        self.SetYtitle("Efficiency")
        
class SpectrumRatioFrame(Frame):
    """
    Frame definition for Spectrum ratio plots
    """
    
    def __init__(self, name, yrange, ytitle):
        """
        Constructor

        :param name: Name of the frame
        :type name: str
        :param yrange: Plot range in y direction (keys min and max required)
        :type yrange: dictionary
        :param ytitle: Title of the y-axis  
        :type ytitle: str
        """
        Frame.__init__(self, name, 0., 100., yrange["min"], yrange["max"])
        self.SetXtitle("p_{t} (GeV/c)")
        self.SetYtitle(ytitle)