#!/usr/bin/env bash

ENV_NAME="/opt/anaconda3/envs/git-toolbox-env"

if [ -x "$(command -v conda)" ]; then
  source activate $ENV_NAME
fi

BASEDIR=$(dirname "$0")
python "$BASEDIR/commit.py" $@