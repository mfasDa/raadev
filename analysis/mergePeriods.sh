#! /bin/bash

SRC=$1
BASE=$2

if [ ! -d $BASE/merged ]; then mkdir $BASE/merged; fi
dirs=($(ls -1 $BASE | grep "LHC"))

. alice_env.sh 1

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
