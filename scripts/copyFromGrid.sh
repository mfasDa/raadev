#!/bin/bash
# $1=path /alice/sim/2013/LHC13b4_plus/ 
# $2=/PWGJE/Jets_EMC_pPb/142_20130911-1655

. alice_env.sh
. /tmp/gclient_env_$UID

BASEDIR=`pwd`

runs=($(alien_ls $1))

for j in `seq 0 10`;
do
    cd $BASEDIR
    mkdir ${runs[$j]}

    for bin in `seq 1 10`;
    do
        ODIR=$(printf "%s/%d/%02d" $BASEDIR ${runs[$j]} $bin)
	      [[ ! -d $ODIR  ]] && mkdir $ODIR
	      cd $ODIR
	      alien_cp alien://$1/${runs[$j]}/$bin/$2/AnalysisResults.root AnalysisResults.root
    done
done

cd $BASEDIR
