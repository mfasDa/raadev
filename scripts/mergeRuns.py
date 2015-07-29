#! /usr/bin/env python
import os, sys

def ExecMerge(outputfile, filelist):
    mergecommand = "hadd -f %s" %(outputfile)
    for gridfile in filelist:
        mergecommand += " %s" %(gridfile) 
    os.system(mergecommand)
    
def GetRunlist(basedir):
    tmplist = os.listdir(basedir)
    runlist = []
    for entry in tmplist:
        if entry.isdigit():
            runlist.append(int(entry))
    return runlist

def GetFilelist(inputpath, runlist, pthardbin, filename):
    result = []
    for r in runlist:
        tmpfile = "%s/%d/%02d/%s" %(inputpath, r, pthardbin, filename)
        if os.path.exists(tmpfile):
            result.append(tmpfile)
    return result

def DoMerge(inputpath, filename):
    mergedir = "%s/merged" %(inputpath)
    runlist = GetRunlist(inputpath)
    basedir = os.getcwd()
    if not os.path.exists(mergedir):
        os.makedirs(mergedir, 0755)
        
    for pthard in range(1, 11):
        print "Merging all file from pt-hard bin %d" %(pthard)
        files = GetFilelist(inputpath, runlist, pthard, filename)
        outputdir = "%s/%02d" %(mergedir, pthard)
        if not os.path.exists(outputdir):
            os.makedirs(outputdir, 0755)
        os.chdir(outputdir)
        ExecMerge(filename, files)
        os.chdir(basedir)
    print "Done"

if __name__ == "__main__":
    inputpath = sys.argv[1]
    rootfile = "AnalysisResults.root"
    if len(sys.argv) > 2:
        rootfile = sys.argv[2]
    DoMerge(inputpath, rootfile)