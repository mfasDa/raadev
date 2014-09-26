#!/bin/bash

. alice_env.sh

BASEDIR=`pwd`

[[ ! -d $BASEDIR/mergeRuns  ]] && mkdir $BASEDIR/mergeRuns

for bin in `seq 1 9`;
do
    binstr=$(printf "%02d" $bin)
    [[ ! -d $BASEDIR/mergeRuns/$binstr  ]] && mkdir $BASEDIR/mergeRuns/$binstr

    cd $BASEDIR/mergeRuns/$binstr

    fls=($(ls $BASEDIR/19*/$binstr/AnalysisResults.root))
    fstring=""
    for f in ${fls[@]}; do
      fstring=$(printf "%s %s" "$fstring" $f) 
    done

    root -b -q ~/Documents/LBL/RAATrigger/mfasel_ptemcaltrigger/macros/LoadLibsAna.C "~/Documents/LBL/RAATrigger/mfasel_ptemcaltrigger/macros/mergeFiles.C(\"AnalysisResults.root\",\"$fstring\")"


    cd $BASEDIR
done

