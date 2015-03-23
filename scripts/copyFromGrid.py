#! /usr/bin/env python

import sys, os, commands, zipfile

def aliencopy(sourcelocation, targetlocation):
    os.system("alien_cp alien://%s %s" %(sourcelocation, targetlocation))
    
def alienlist(directory):
    return commands.getstatusoutput("alien_ls %s" %(directory))

def transfer(trainrun, outputlocation, targetfile, outputfile):
    sample = "/alice/sim/2013/LHC13b4_plus"
    runlist =  alienlist(sample)
    for r in runlist:
        for b in range(1, 11):
            inputpath = "%s/%d/%d/%s/%s" %(sample, r, b, trainrun, targetfile)
            outputdir = "%s/%d/%0d/" 
            if not os.path.exists(outputdir):
                os.makedirs(outputdir, 0755)
            aliencopy(inputpath, "%s/%s" %(outputdir, targetfile))
            
            if "zip" in targetfile:
                cwd = os.getcwd()
                os.chdir(outputdir)
                #unzip
                myarchive = zipfile.ZipFile(targetfile)
                myarchive.extractall()
                os.chdir(cwd)

if __name__ == "__main__":
    trainrun = sys.argv[1] 
    outputfile = "root_archive.zip"
    if len(sys.argv) > 3:
        outputfile = sys.argv[3]
    transfer(trainrun, outputfile)