#! /bin/bash

SCRIPTPATH=$(readlink -f $(dirname $0))
SRC=$SCRIPTPATH/..
BASE=$1

if [ ! -d $BASE/merged ]; then mkdir $BASE/merged; fi
dirs=($(ls -1 $BASE | grep "LHC"))

isFirst=1
inputfiles=
for d in ${dirs[@]}; do
        if [ $isFirst -gt 0 ]; then
                inputfiles=$(printf "%s/%s/AnalysisResults.root" $BASE $d)
                isFirst=0
        else
                inputfiles=$(printf "%s %s/%s/AnalysisResults.root" "$inputfiles" $BASE $d)
        fi
done
cmd=$(printf "root -b -q %s/macros/LoadLibsAna.C \'%s/macros/mergeFiles.C(\"%s/merged/AnalysisResults.root\",\"%s\")\'" $SRC $SRC $BASE "$inputfiles")
echo $cmd
eval $cmd
