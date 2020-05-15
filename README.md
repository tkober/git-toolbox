# git-toolbox

This repository contains a bunch of more sophisticated versions of common git command line tools.

## Prerequireties

In order do install or run this tool make sure either PIP or Anaconda is installed and available on your bash.


## Install

The repository's root directory contains a bash script for installation.

`bash install.sh`

#### Caution

Some packages will be installed during the installation. If anaconda is available a seperate environment will be created. If anaconda is not found pip will be used instead. This could lead to overwriting existing packages or versions. The usage of anaconda is highly recommended. You can get it [here](https://www.anaconda.com/).

## git-stage

This tool implements an interactive and more sophisticated version of git-status.

![screenshot](doc/screenshot_stage.png)

### Run

After installation _git-stage_ is available in your bash using the following command:

`stage [PATH]`

If no path is provided the current directory will be used.
