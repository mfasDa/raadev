#! /usr/bin/env python

import os, sys, getopt

if __name__ == "__main__":
    # extract directory path, and add it if necessary to the PythonPath
    distribution = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
    paths = os.getenv("PYTHONPATH").split(":")
    found = False
    for path in paths:
        if os.path.abspath(path) == "distribution":
            found = True
            break
    if not found:
        sys.path.append(distribution)
        
from write.StrippedFileCreator import ConvertTrainFile, isPythiaHard

def FindRecursive(filename, inputdir):
    result = []
    for dirpath, dirnames, files in os.walk(inputdir):
        # Go through the directory and look for files there
        for mydir in dirnames:
            found = FindRecursive(filename, os.path.join(dirpath, mydir))
            for f in found:
                result.append(f)
        # Now check files whether they match in the name
        for myfile in files:
            if filename == os.path.basename(myfile):
                result.append(os.path.join(dirpath, filename))
    return result

if __name__ == "__main__":
    filename = sys.argv[1]
    isPythiaHard = False
    rootfile = None
    if len(sys.argv) > 2:
        opts, args = getopt.getopt(sys.argv[2:], "r:p")
        for o,a in opts:
            if o == "-r":
                rootfile = str(a)
            elif o == "-p":
                isPythiaHard == True
    files = FindRecursive(filename, os.getcwd())
    for f in files:
        myfile = f
        if rootfile:
            myfile += "#%s" %rootfile
        print "Converting inputfile %s" %myfile
        ConvertTrainFile(sys.argv, isPythiaHard)
