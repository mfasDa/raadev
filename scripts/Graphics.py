#! /usr/bin/env python

"""
Graphics.py
 Created on: 28.08.2014
     Author: markusfasel
     
Graphics module, containing basic ROOT plot helper functionality
"""

class Frame:
        """
        Helper class handling frame drawing in plots
        """
    
        def __init__(self, name, min, max, ymin, ymax):
                self.__framehist = TH1F(name, "", 100, min, max)
                self.__framehist.SetStats(False)
                self.__framehist.GetYaxis().SetRangeUser(ymin, ymax)
                        
        def SetXtitle(self, title):
                self.__framehist.GetXaxis().SetTitle(title)
    
        def SetYtitle(self, title):
                self.__framehist.GetYaxis().SetTitle(title)
        
        def Draw(self):
                self.__framehist.Draw("axis")

class Style:
        """ 
        
        Class for plot styles (currently only color and marker)
        """
        def __init__(self, color, marker):
                self.__color = color
                self.__marker = marker

        def SetColor(self, color):
                self.__color = color

        def SetMarker(self, marker):
                self.__marker = marker

        def GetColor(self):
                return self.__color

        def GetMarker(self):
                return self.__marker

