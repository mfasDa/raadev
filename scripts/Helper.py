#! /usr/bin/python
#
# Helper tools for spectrum plotting
#

def NormaliseBinWidth(hist):
        """
        Normalise each bin by its width
        """
        for mybin in range(1,hist.GetXaxis().GetNbins()):
                bw = hist.GetXaxis().GetBinWidth(mybin)
                hist.SetBinContent(mybin, hist.GetBinContent(mybin)/bw)
                hist.SetBinError(mybin, hist.GetBinError(mybin)/bw)
