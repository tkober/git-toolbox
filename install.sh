#!/usr/bin/env bash

ENV_NAME="git-stage-env"
YML_FILE="environment.yml"
PIP_FILE="environment.txt"
RUN_SCRIPT="run.sh"
FUNCTION_NAME="stage"
BASEDIR=$(cd "$(dirname "$0")/"; pwd)

if [ -x "$(command -v conda)" ]; then
    conda env create --name $ENV_NAME --file $YML_FILE --force
  else
  	echo "WARNING: Conda not available, falling back to pip"
  	echo "Some python packages need to be installed. These might overwrite your existing base environment packages and can cause trouble."

  	read -p "Do you want to continue without conda (y/[n])? " -n 1 -r
	echo
	if [[ $REPLY =~ ^[Yy]$ ]]
	then
		pip install -r $PIP_FILE
	else
		exit
	fi
fi

echo "function $FUNCTION_NAME { $BASEDIR/$RUN_SCRIPT \$1; }" >> ~/.bash_profile
clear