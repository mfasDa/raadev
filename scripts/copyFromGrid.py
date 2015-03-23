#! /usr/bin/env python

import sys, os, commands, zipfile

def aliencopy(sourcelocation, targetlocation):
    os.system("alien_cp alien://%s %s" %(sourcelocation, targetlocation))
    
def alienlist(directory):
    runlist = []
    tmplist = commands.getstatusoutput("alien_ls %s" %(directory))[1].split("\n")
    for r in tmplist:
        runlist.append(int(r.lstrip().rstrip()))
    return runlist

def transfer(trainrun, outputlocation, targetfile):
    sample = "/alice/sim/2013/LHC13b4_plus"
    runlist =  alienlist(sample)
    for r in runlist:
        print "Doing run %s" %(r)
        for b in range(1, 11):
            inputpath = "%s/%d/%d/%s/%s" %(sample, r, b, trainrun, targetfile)
            outputdir = "%s/%d/%02d/" %(outputlocation, r, b)
            if not os.path.exists(outputdir):
                os.makedirs(outputdir, 0755)
            aliencopy(inputpath, "%s/%s" %(outputdir, targetfile))
            
            if "zip" in targetfile and os.path.exists("%s/%s" %(outputdir, targetfile)):
                cwd = os.getcwd()
                os.chdir(outputdir)
                #unzip
                myarchive = zipfile.ZipFile(targetfile)
                myarchive.extractall()
                os.chdir(cwd)

if __name__ == "__main__":
    trainrun = sys.argv[1] 
    outputpath = sys.argv[2]
    outputfile = "root_archive.zip"
    if len(sys.argv) > 3:
        outputfile = sys.argv[3]
    transfer(trainrun, outputpath, outputfile)