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
Interpolation module

:organization: ALICE Collaboration
:copyright: 1998-2014, ALICE Experiment at CERN, All rights reserved.

Original author (ROOT macro):

:author: Jacek Otwinowski
:organization: ALICE Collaboration

Translated into PYTHON by  

:author: Markus Fasel
:contact: markus.fasel@cern.ch
:organization: Lawrence Berkeley National Laboratory
"""
import math

class Interpolator(object):
    
    def __init__(self, dodebug = False):
        """
        Constructor
        
        :param dodebug: If true then debug messages are printed
        :type dodebug: bool
        """
        self.__doDebug = dodebug
    
    def Interpolate(self, x, x1, y1, x2, y2, integrate = False, r = 0, method="lin"):
        """
        Interpolation handler:
        forwards methods to the different interpolation functions
        Interpolation methods are:
            - lin: linear interpolation
            - pow: power law interpolation
            - exp: exponential interpolation
            - hag: modified hagedorn interpolation
        
        :param x:  x at which to evaluate the interpolation 
        :param x1: lower x step
        :param y1: function value at x1
        :param x2: upper x step
        :param y2: function value at x2
        :param integrate: if true we evaluate the integral
        :param r: 
        :type x: float
        :type x1: float
        :type y1: float
        :type x2: float
        :type y2: float
        :type r: float
        :type integrate: bool
        :return: interpolated value
        :rtype: float
        """ 
        if method == "lin":
            return self.__InterpolateLinear(x, x1, y1, x2, y2, integrate, r)
        elif method == "pow":
            return self.__InterpolatePowerLaw(x, x1, y1, x2, y2, integrate, r)
        elif method == "exp":
            return self.__InterpolateExponential(x, x1, y1, x2, y2)
        elif method == "hag":
            return self.__InterpolateSimpleHagedorn(x, x1, y1, x2, y2)

    def __InterpolateLinear(self, x, x1, y1, x2, y2, integrate = False, r = 0):
        """
        Linear interpolation method

        :param x:  x at which to evaluate the interpolation 
        :param x1: lower x step
        :param y1: function value at x1
        :param x2: upper x step
        :param y2: function value at x2
        :param integrate: if true we evaluate the integral
        :param r: 
        :type x: float
        :type x1: float
        :type y1: float
        :type x2: float
        :type y2: float
        :type r: float
        :type integrate: bool
        :return: interpolated value
        :rtype: float
        """ 
        if x1-x2 == 0:
            return 0
        if integrate:
            return 2*r*(y1+((x-x1)*(y1-y2))/(x1-x2))
        else:
            return (y1 + (((y2-y1)/(x2-x1))*(x-x1))) 
        

    def __InterpolatePowerLaw(self, x, x1, y1, x2, y2, integrate = False, r = 0):
        """
        Power law interpolation method

        :param x:  x at which to evaluate the interpolation 
        :param x1: lower x step
        :param y1: function value at x1
        :param x2: upper x step
        :param y2: function value at x2
        :param integrate: if true we evaluate the integral
        :param r: 
        :type x: float
        :type x1: float
        :type y1: float
        :type x2: float
        :type y2: float
        :type r: float
        :type integrate: bool
        :return: interpolated value
        :rtype: float
        """ 
        #assume functional form y=a*x^n
        if not self.__AssurePositive(x, x1, x2, y1, y2):
            return 0.
 
        n = (math.log(y1)-math.log(y2))/(math.log(x1)-math.log(x2))
        a = y1*math.pow(x1,-n)

        if self.__doDebug:
            print "x: %f, steps: (%f, %e) and (%f, %e)" %(x, x1, y1, x2, y2)
            print "y: %e" %(a*math.pow(x,n))
            print "n: %f" %(n)
            print "a: %f" %(a)

        if integrate: 
            return  ((a/(n+1.))*(pow(x+r,n+1.)-pow(x-r,n+1.))/(2.*r))
        else:
            return a*math.pow(x,n)

    def __InterpolateExponential(self, x, x1, y1, x2, y2):
        """
        Exponential interpolation method

        :param x:  x at which to evaluate the interpolation 
        :param x1: lower x step
        :param y1: function value at x1
        :param x2: upper x step
        :param y2: function value at x2
        :type x: float
        :type x1: float
        :type y1: float
        :type x2: float
        :type y2: float
        :return: interpolated value
        :rtype: float
        """ 
        if not self.__AssurePositive(x, x1, x2, y1, y2):
            return 0.
        return math.exp(self.__InterpolateLinear(x,x1,math.log(y1),x2,math.log(y2)))

    def __InterpolateSimpleHagedorn(self, x, x1, y1, x2, y2):
        """
        Hagedorn interpolation method
        
        :param x:  x at which to evaluate the interpolation 
        :param x1: lower x step
        :param y1: function value at x1
        :param x2: upper x step
        :param y2: function value at x2
        :type x: float
        :type x1: float
        :type y1: float
        :type x2: float
        :type y2: float
        :return: interpolated value
        :rtype: float
        """ 
        
        if not self.__AssurePositive(x, x1, x2, y1, y2):
            return 0.
        return math.exp(self.__InterpolateLinear(math.log(1.+x),math.log(1.+x1),math.log(y1),math.log(1.+x2),math.log(y2)))
    
    def __AssurePositive(self, x, x1, x2, y1, y2):
        """
        Check if all values are positive
        
        :param x: x-coordiate
        :param x1: x-coordiate of the lower point
        :param x2: x-coordiate of the upper point
        :param y1: y-coordiate of the lower point
        :param y2: y-coordiate of the upper point
        :type x: float
        :type x1: float
        :type y1: float
        :type x2: float
        :type y2: float
        :return: true if all values are positive, false otherwise
        :rtype: bool
        """
        if x <= 0. or x1 <= 0. or x2 <= 0. or y1 <= 0. or y2 <= 0.:
            return False
        return True
