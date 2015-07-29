#!/bin/bash
if  [ "x$HOSTNAME" == "xlbnl5core" ]; then
	source /usr/share/Modules/inits/bash
	module use /home/markus/modulefiles
	module load markus/alien/v2-19
else
	. alice_env.sh
fi

BASEDIR=`pwd`
SCRIPTDIR=$(readlink -f `dirname $0`)
SOURCEDIR=`dirname $SCRIPTDIR` 

[[ ! -d $BASEDIR/mergeRuns  ]] && mkdir $BASEDIR/mergeRuns

for bin in `seq 1 10`;
do
    binstr=$(printf "%02d" $bin)
    [[ ! -d $BASEDIR/mergeRuns/$binstr  ]] && mkdir $BASEDIR/mergeRuns/$binstr

    cd $BASEDIR/mergeRuns/$binstr

    fls=($(ls $BASEDIR/19*/$binstr/AnalysisResults.root))
    fstring=""
    for f in ${fls[@]}; do
      fstring=$(printf "%s %s" "$fstring" $f) 
    done

    cmd=$(printf "root -b -q %s/macros/LoadLibsAna.C \'%s/macros/mergeFiles.C(\"AnalysisResults.root\",\"%s\")\'" $SOURCEDIR $SOURCEDIR "$fstring")
	eval $cmd
	
    cd $BASEDIR
done

