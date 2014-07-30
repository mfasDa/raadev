#! /usr/bin/python
import os, sys, getopt
from ROOT import TCanvas,TFile,TH1F,TPaveText,gROOT,kRed
from Helper import NormaliseBinWidth

gObjects = list()

class FileReaderException(Exception):
        def __init__(self, filename):
                self.__filename == filename

        def __str__(self):
                return "Could not open file %s" %(filename)

class HistNotFoundException(Exception):
        def __init__(self, histname):
                self.__histname = histname

        def __str__(self):
                return "Histogram %s not found" %(histname)

def ReadFromFile(filename, options):
        infile = TFile.Open(filename)
        if not infile or infile.IsZombie():
                raise FileReaderException(filename)
        resultlist = infile.Get("results")
        histlist = resultlist.FindObject("List of histograms of container PtEMCalTriggerHistograms")

        resultlist = dict()
        histnameEC = "hEvents%s" %(options["Trigger"])
        histnameSpec = "hPt%s_%s_%s" %(options["Trigger"], options["Eventselection"], options["Trackselection"])
        hEC = histlist.FindObject(histnameEC)
        if not hEC:
                infile.Close()
                raise HistNotFoundException(histnameEC)
        else:
                hEC.SetDirectory(gROOT)
                resultlist["EventCounter"] = hEC
        hSpec = histlist.FindObject(histnameSpec)
        if not hSpec:
                hSpec.SetDirectory(gROOT)
                infile.Close()
                raise HistNotFoundException(histnameSpec)
        else:
                resultlist["Spectrum"] = hSpec
        return resultlist

def MakePlot(spectrum, options):
        plot = TCanvas("crawspectrum", "Raw charged hadron spectrum")
        plot.cd()
        plot.SetGrid(False, False)
        plot.SetLogx()
        plot.SetLogy()

        axes = TH1F("axis", "; p_{T} (GeV/c); 1/N_{ev} dN/dp_{t} ((GeV/c)^{-1})", 1000, 0., 100.)
        axes.SetStats(False)
        axes.GetYaxis().SetRangeUser(1e-9, 100)
        axes.Draw("axis")
        gObjects.append(axes)

        spectrum.SetMarkerColor(kRed)
        spectrum.SetLineColor(kRed)
        spectrum.SetMarkerStyle(24)
        spectrum.Draw("epsame")
        gObjects.append(spectrum)

        label = TPaveText(0.65, 0.7, 0.89, 0.89, "NDC")
        label.SetBorderSize(0)
        label.SetFillStyle(0)
        label.SetTextAlign(12)
        cutstring = "ON"
        if options["Trackselection"] == "nocut":
                cutstring = "OFF"
        prstring = "ON"
        if options["Eventselection"] == "nopr":
                prstring = "OFF"
        label.AddText("Trigger:          %s" %(options["Trigger"]))
        label.AddText("Standard cuts:    %s" %(cutstring))
        label.AddText("Pileup rejection: %s" %(prstring))
        label.Draw()
        gObjects.append(label)

        gObjects.append(plot)
        return plot

def Usage():
        print " Usage: "
        print "   "
        print "   DrawRawSpectrum.py [OPTIONS] filename"
        print "   "
        print " Options:"
        print "   -e/--emcal [1:4]:         Use EMCal triggered events. The number is the trigger type"
        print "                  1:         EMCal Jet High Threshold"
        print "                  2:         EMCal Jet Low Threshold"
        print "                  3:         EMCal Gamma High Threshold"
        print "                  4:         EMCal Gamma Low Threshold"
        print "   -h/--help:                Print help text"
        print "   -m/--minbias:             Use min. bias events"
        print "   -n/--nocuts:              No cuts applied"
        print "   -o/--outputfile name:     Write spectrum to output file"
        print "   -p/--plotname name:       Write plot to output file"
        print "   -s/--standardcuts:        Apply standard cuts"
        print "   -r/--pilupreject:         Pileup rejection applied"
        print "   -w/--withpilup:           No pileup rejection applied"

def launch(filename, options):
        try:
                speclist = ReadFromFile(filename, options);
        except FileReaderException as e:
                print str(e)
                sys.exit(1)
        except HistNotFoundException as e:
                print str(e)
                sys.exit(1)

        nevents = 0
        if options["eventselection"] == "nopr":
                nevents = speclist["EventCounter"].GetBinContent(1)
        else:
                nevents = speclist["EventCounter"].GetBinContent(2)

        spectrum = speclist["Spectrum"].ProjectionY("rawspectrum")
        spectrum.Sumw2()
        spectrum.Scale(1./nevents)
        NormaliseBinWidth(spectrum)

        plot = MakePlot(spectrum, options)
        if len(options["plotfile"]):
                plot.SaveAs(options["plotfile"])
        if len(options["outputfile"]):
                outputfile = TFile(options["outputfile"], "RECREATE")
                if outputfile:
                        outputfile.cd()
                        spectrum.Write(spectrum.GetName())
                        outputfile.Close()

def main():
        if len(sys.argv) < 2:
                Usage()
                sys.exit(1)

        filename = sys.argv[len(sys.argv) - 1]
        
        try:
                opt, arg = getopt.getopt(sys.argv[1:], "e:mno:p:rsw", ["emcal=","help","minbias","nocuts","outputfile=","plotname=","standardcuts","pileupreject","withpileup"])
        except getopt.GetoptError as e:
                print "Invalid argument(s)"
                print str(e)
                sys.exit(1)

        options = dict()
        # Set defaults
        options["Trigger"]            = "MinBias"
        options["Trackselection"]     = "stdcut"
        options["Eventselection"]     = "wpr"
        options["plotfile"]           = ""
        options["outputfile"]         = ""

        for o,a in opt:
                if o in ("--e", "--emcal"):
                        emcalTrigger = int(a)
                        if not emcalTrigger in range(1,5):
                                print "EMCal Trigger invalid"
                                Usage()
                                sys.exit(1)
                        else:
                                if emcalTrigger == 1:
                                        options["Trigger"] = "EMCJHigh"
                                elif emcalTrigger == 2:
                                        options["Trigger"] = "EMCJLow"
                                elif emcalTrigger == 3:
                                        options["Trigger"] = "EMCGHigh"
                                elif emcalTrigger == 4:
                                        options["Trigger"] = "EMCGLow"
                elif o in ("-h", "--help"):
                        Usage()
                        sys.exit(1)
                elif o in ("-m", "--minBias") :
                        options["Trigger"] = "MinBias"
                elif o in ("-n", "--nocuts") :
                        options["Trackselection"] = "nocut"
                elif o in ("-o", "--outputfile"):
                        options["outputfile"] = str(a)
                elif o in ("-p", "--outputfile"):
                        options["plotfile"] = str(a)
                elif o in ("-s", "--standardcuts"):
                        options["Trackselection"] = "stdcut"
                elif o in ("-r", "-pileupreject"):
                        options["eventselection"] = "wpr"
                elif o in ("-w", "-withpileup"):
                        options["eventselection"] = "nopr"

        launch(filename, options)

if __name__ == "__main__":
        main()
