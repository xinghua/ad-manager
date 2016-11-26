#!/usr/bin/env bash

#USER=`whoami`
#GROUP=`id -gn $USER`

USER=xinghua
GROUP=xinghua

PROJECT_PATH=/home/xinghua/project
SPM_PATH=spm

if [ "$#" -lt 1 ]; then
    echo "usage:"
    echo "      cmd [adlog,admin]"
    exit 1
fi

DIST=$1

if [ "$DIST" = "adlog" ]; then
    PREFIX=$PROJECT_PATH/ad-adlog
elif [ "$DIST" = "admin" ]; then
    PREFIX=$PROJECT_PATH/ad-admin
else
    echo "bad dist, choose [adlog,admin]"
    exit 1
fi

cmd="./install.sh --user=$USER --group=$GROUP --prefix=$PREFIX  --mode=$1"
eval $cmd
