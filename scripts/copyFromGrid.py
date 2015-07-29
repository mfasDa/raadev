#! /usr/bin/env python

import sys, os, commands, zipfile

def aliencopy(sourcelocation, targetlocation):
    print "Copy %s to %s" %(sourcelocation, targetlocation)
    os.system("alien_cp alien://%s %s" %(sourcelocation, targetlocation))
    
def alienlist(inputdir):
    print "Scanning directory: %s" %(inputdir)
    runlist = []
    tmplist = commands.getstatusoutput("alien_ls %s" %(inputdir))[1].split("\n")
    for r in tmplist:
        runlist.append(r.lstrip().rstrip())
    return runlist

def extractZipfile(filename):
    if not ".zip" in filename or not os.path.exists(filename):
        return
    cwd = os.getcwd()
    os.chdir(os.path.dirname(filename))
    #unzip
    myarchive = zipfile.ZipFile(os.path.basename(filename))
    myarchive.extractall()
    os.chdir(cwd)
    
def TransferFile(inputfile, outputfile):
    if not os.path.exists(os.path.dirname(outputfile)):
        os.makedirs(os.path.dirname(outputfile), 0755)
    aliencopy(inputfile, outputfile)
    extractZipfile(outputfile)
    

def transferMergingStage(inputpath, outputpath, targetfile):
    dirs = alienlist(inputpath)
    for indir in dirs:
        if not indir.isdigit():
            continue
        inputfile = "%s/%s/%s" %(inputpath, indir, targetfile) 
        outputfile = "%s/%s/%s" %(outputpath, indir, targetfile)
        TransferFile(inputfile, outputfile)

def transfer(trainrun, outputlocation, targetfile):
    sample = "/alice/sim/2013/LHC13b4_plus"
    runlist =  alienlist(sample)
    for r in runlist:
        if not r.isdigit():
            continue
        print "Doing run %s" %(r)
        for b in range(1, 11):
            inputdir= ("%s/%d/%d/%s" %(sample, int(r), b, trainrun))
            inputfile = "%s/%s" %(inputdir, targetfile)
            outputdir = os.path.abspath("%s/%d/%02d" %(outputlocation, int(r), b))
            outputfile = "%s/%s" %(outputdir, targetfile)
            if not os.path.exists(outputfile):
                TransferFile(inputfile, outputfile)
                
            # copy stage files
            outputlist = alienlist(inputdir)
            for content in outputlist:
                if not "Stage" in content or ".xml" in content:
                    continue
                print "Copying %s" %(os.path.basename(content))
                stagedir = "%s/%s" %(outputdir, os.path.basename(content))
                if not os.path.exists(stagedir):
                    os.mkdir(stagedir, 0755)
                transferMergingStage(inputdir, stagedir, targetfile)

if __name__ == "__main__":
    trainrun = sys.argv[1] 
    outputpath = sys.argv[2]
    outputfile = "root_archive.zip"
    if len(sys.argv) > 3:
        outputfile = sys.argv[3]
    transfer(trainrun, outputpath, outputfile)