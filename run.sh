#!/usr/bin/env bash

ENV_NAME="git-stage-env"

if [ ! -z "$1" ]
  then
    cd $1
fi

if [ -x "$(command -v conda)" ]; then
  source activate $ENV_NAME
fi

BASEDIR=$(dirname "$0")
python "$BASEDIR/app.py"