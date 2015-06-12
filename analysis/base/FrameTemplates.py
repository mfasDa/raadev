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
import math

class NormalizedPtSpectrumFrame(Frame):
    """
    Frame definition for fully normalized p-t spectrum
    """

    def __init__(self, name, ptmin = 0):
        """
        Constructor

        :param name: Name of the frame
        :type name: str
        """
        Frame.__init__(self, name, ptmin, 100., 1e-12, 10)
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
        
        
class AdjustableRangeFrame(Frame):
    """
    Frame which auto-adjusts the range to the data range of the graphics objects within.
    Needs a data range provided from outside
    """
    
    def __init__(self, name, datarange, titles):
        """
        Constructor
        
        :param name: Name of the fram
        :type name: str
        :param datarange: min. and max. value of the data within the frame in both coordinates
        :type datarange: dictionary
        :param titles: Title of the x and y axis
        :type titles: dictionary
        """
        xmin = self.__DeterminePlotRange("MIN", datarange["xmin"])
        ymin = self.__DeterminePlotRange("MIN", datarange["ymin"])
        xmax = self.__DeterminePlotRange("MAX", datarange["xmax"])
        ymax = self.__DeterminePlotRange("MAX", datarange["ymaxs"])
        Frame.__init__(self, name, xmin, xmax, ymin, ymax)
        self.SetXtitle(titles["xtitle"])
        self.SetYtitle(titles["ytitle"])
    
    def __DeterminePlotRange(self, direction, datarange):
        """
        Determin the plot range, defined as always +1 / -1 of the subleading digit from the maximum / minimum
        
        :param direction: direction (MIN or MAX)
        :type direction: str
        :param datarange: minimum or maximum of the data
        :type datarange: int, float
        :return: plot range
        :rtype: float
        """
        power = self.__GetPower(datarange)
        # print "Power: %d" %power
        lead = self.__GetLeading(datarange)
        # print "Leading: %d" %lead
        sub = self.__GetNextSub(datarange)
        sub = sub + 1 if direction == "MAX" else sub -1
        # print "Subleading: %d" %sub
        return (lead*10+sub) * pow(10, power-1)
    
    def __GetPower(self, number):
        """
        Get the number of digit
        
        :param number: number to check
        :type numer: int, float
        :return: Number of digits
        :rtype: int
        """
        test = 10
        power = 0
        absnumber = math.fabs(number)
        if absnumber > 1:
            # larger than 1 - power positive
            success = (absnumber // test) > 0
            if success:
                power = 1
                while success:
                    test *= 10
                    success = (absnumber // test) > 0
                    if success:
                        power += 1
        else:
            # between 0 and 1
            datatest = absnumber
            negativepower = 1
            found = False
            while not found:
                datatest *= 10
                if datatest >= 1:
                    found = True
                else:
                    negativepower += 1
            power = -1 * negativepower
        return power

    def __GetLeading(self, number):
        """
        Get the leading digit
        
        :param number: Number to check
        :type number: int, float
        :return: Leading digit
        :rtype: int
        """
        power = self.__GetPower(number)
        if power >= 0:
            test = pow(10, power)
            stripped = number // test
            return stripped %10
        else:
            return int(number * pow(10, power))
  
    def __GetNextSub(self, number):
        """
        Get the subleading digit
        
        :param number: Number to check
        :type number: int, float
        :return: Leading digit
        :rtype: int
        """
        power = self.__GetPower(number)
        if power >= 0:
            test = pow(10, power - 1)
            stripped = number // test
            return stripped %10
        else:
            test = int(number * pow(10, power+1))
            return tests % 10
