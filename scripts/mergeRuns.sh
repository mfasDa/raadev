#!/bin/bash

. alice_env.sh

BASEDIR=`pwd`
SCRIPTIDR=$(readlink -f `dirname $0`)
SOURCEDIR=`dirname $SCRIPTDIR` 

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

    cmd=$(printf "root -b -q %s/macros/LoadLibsAna.C \"%s/macros/mergeFiles.C(\"AnalysisResults.root\",\"%s\")\"" $SOURCEDIR $SOURCEDIR $fstring)
	eval $cmd
	
    cd $BASEDIR
done

