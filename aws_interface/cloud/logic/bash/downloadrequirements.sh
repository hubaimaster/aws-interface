#!/usr/bin/env bash
cd $1
pip download -d $2 -r requirements.txt
cd ..
cd $2
unzip -o \*.whl
rm -r *.whl
echo "Complete download and unzip packages in [$1] requirements to [$2]"