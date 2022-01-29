#!/bin/bash
rm -rf venv 2> /dev/null
if [ ! command -v pip &> /dev/null ] 
then
	echo "You should install pip before running this script!"
	exit
fi

pip install virtualenv
virtualenv venv
. venv/bin/activate
echo $VIRTUAL_ENV
pip install cfn-lint
npm install -D sls-dev-tools
