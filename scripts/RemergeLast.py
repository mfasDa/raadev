#!  /usr/bin/env python 

import getpass, os, shutil, sys

def MergeBucket(outputfile, listoffiles):
    mergecommand = "hadd -f %s" %(outputfile)
    for f in listoffiles:
        mergecommand += " %s" %(f)
    os.system(mergecommand)
    
def RecursiveMerge(outputfile, listoffiles, bucketfactor, sandbox, iteration = 0):
    if not os.path.exists(sandbox):
        os.makedirs(sandbox, 0755)
    stagedir = "%s/iter%d" %(sandbox, iteration)
    rootfile = os.path.basename(outputfile)
    listfornext = []
    patchcounter = 0
    package = []
    for f in listoffiles:
        package.append(f)
        if len(package) >= bucketfactor:
            mergedfile = "%s/%d/%s" %(stagedir, patchcounter, rootfile)
            MergeBucket(mergedfile, listoffiles)
            patchcounter +=1
            package = []
            listfornext.append(mergedfile)
    # merge last bunch
    if len(package):
        mergedfile = "%s/%d/%s" %(stagedir, patchcounter, rootfile)
        MergeBucket(mergedfile, listoffiles)
        listfornext.append(mergedfile)
    if len(listfornext) == 1:
        # we are done
        # move output file to its final location
        # clean sandbox
        shutil.move_file(listfornext[0], outputfile)    
        os.rmdir(sandbox)
    else:
        # next iteration step
        RecursiveMerge(outputfile, listfornext, bucketfactor, sandbox, iteration+1)
        
def FindListStage(inputdirs):
    maxID = -1
    for f in inputdirs:
        if not "Stage_" in inputdirs:
            continue
        stageID = int(f.replace("Stage_", ""))
        if stageID > maxID:
            maxID = stageID
    if maxID > -1:
        return "Stage_%s" %(maxID)
    return None

def FindRecursive(inputpath, rootfilename):
    result = []
    dirpath, dirlist, files = os.walk(inputdir)
    for f in files:
        if f == rootfilename:
            result.append("%s/%s" %(inputpath,f))
    for d in dirlist:
        tmplist = FindRecursive("%s/%s" %(inputpath, d), rootfilename)
        for f in tmplist:
            result.append(f)
    return result

def RunMerge(inputdir, rootfile):
    for r in os.listdir(inputdir):
        for b in os.listdir("%s/%s" %(inputdir, r)):
            stageToMerge = FindLastStage(os.listdir("%s/%s/%s" %(inputdir, r, b)))
            inputdir = "%s/%s/%s/%s" %(inputdir, r, b, stageToMerge)
            outputfile = "%s/%s/%s/%s" %(inputdir, r, b, rootfile)
            if stageToMerge:
                # create filelist
                print "merging run %s, bin %s" %(r, b)
                RecursiveMerge(outputfile, FindRecursive(inputdir, rootfile), 10, "/tmp/%s/merge" %(getpass.getuser()))
                
if __name__ == "__main__":
    RunMerge(sys.argv[1], sys.argv[2])