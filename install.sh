#!/usr/bin/env bash

ENV_NAME="git-toolbox-env"
YML_FILE="environment.yml"
PIP_FILE="environment.txt"

STAGE_RUN_SCRIPT="stage.sh"
STAGE_FUNCTION_NAME="stage"

COMMIT_RUN_SCRIPT="commit.sh"
COMMIT_FUNCTION_NAME="commit"

BRANCHES_RUN_SCRIPT="branches.sh"
BRANCHES_FUNCTION_NAME="branches"

BASEDIR=$(cd "$(dirname "$0")/"; pwd)

if [ -x "$(command -v conda)" ]; then
    conda env create --name $ENV_NAME --file $YML_FILE --force
  else
  	tput setaf 1; tput bold; echo "WARNING: Conda not available, falling back to pip"; tput sgr0;
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

echo "function $STAGE_FUNCTION_NAME { $BASEDIR/$STAGE_RUN_SCRIPT \$@; }" >> ~/.bash_profile
echo "function $COMMIT_FUNCTION_NAME { $BASEDIR/$COMMIT_RUN_SCRIPT \$@; }" >> ~/.bash_profile
echo "function $BRANCHES_FUNCTION_NAME { $BASEDIR/$BRANCHES_RUN_SCRIPT \$@; }" >> ~/.bash_profile


clear
tput setaf 2; tput bold; echo "Installation successful!"; tput sgr0;
echo ""
echo "Make all commands available on your shell by running:"
echo ""
tput setaf 6; echo "    source ~/.bash_profile"; tput sgr0;
echo ""