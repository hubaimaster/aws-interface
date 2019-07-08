#!/usr/bin/env bash
cd $1
pip download -d $1 -r requirements.txt
unzip -o \*.whl
rm -r *.whl
echo "Complete download and unzip packages to [$1]"