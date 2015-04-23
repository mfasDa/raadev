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
    if not os.path.exists(stagedir):
        os.mkdir(stagedir)
    rootfile = os.path.basename(outputfile)
    listfornext = []
    patchcounter = 0
    package = []
    for f in listoffiles:
        if os.path.exists(f):
            print "Adding file %s" %f
            package.append(f)
        if len(package) >= bucketfactor:
            mergedfile = "%s/%d/%s" %(stagedir, patchcounter, rootfile)
            os.makedirs(os.path.dirname(mergedfile), 0755)
            MergeBucket(mergedfile, package)
            patchcounter +=1
            package = []
            listfornext.append(mergedfile)
    # merge last bunch
    if len(package):
        mergedfile = "%s/%d/%s" %(stagedir, patchcounter, rootfile)
        os.makedirs(os.path.dirname(mergedfile), 0755)
        MergeBucket(mergedfile, listoffiles)
        listfornext.append(mergedfile)
    if len(listfornext) == 1:
        # we are done
        # move output file to its final location
        # clean sandbox
        shutil.move(listfornext[0], outputfile)    
        os.rmdir(sandbox)
    else:
        # next iteration step
        RecursiveMerge(outputfile, listfornext, bucketfactor, sandbox, iteration+1)
        
def FindLastStage(inputdirs):
    maxID = -1
    for f in inputdirs:
        print f
        if not "Stage_" in f:
            continue
        stageID = int(f.replace("Stage_", ""))
        if stageID > maxID:
            maxID = stageID
    if maxID > -1:
        return "Stage_%s" %(maxID)
    return None

def FindRecursive(inputpath, rootfilename):
    result = []
    for dirpath, dirlist, files in os.walk(inputpath):
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
        print "Doing run %s" %r
        for b in os.listdir("%s/%s" %(inputdir, r)):
            print "Doing bin %s" %b
            stageToMerge = FindLastStage(os.listdir("%s/%s/%s" %(inputdir, r, b)))
            if stageToMerge:
                # create filelist
                print "merging run %s, bin %s" %(r, b)
                mergeinputdir = "%s/%s/%s/%s" %(inputdir, r, b, stageToMerge)
                outputfile = "%s/%s/%s/%s" %(inputdir, r, b, rootfile)
                RecursiveMerge(outputfile, FindRecursive(mergeinputdir, rootfile), 10, "/tmp/%s/merge" %(getpass.getuser()))
                
if __name__ == "__main__":
    RunMerge(sys.argv[1], sys.argv[2])