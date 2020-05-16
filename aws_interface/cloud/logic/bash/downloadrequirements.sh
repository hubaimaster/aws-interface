#!/usr/bin/env bash
cd $1
pip install requirements.txt -t $2
pip download -d $2 -r requirements.txt
cd ..
cd $2
unzip -o \*.whl
for a in `ls -1 *.tar.gz`; do gzip -dc $a | tar xf -; done
rm -r *.whl
rm -r *.gz
rm -r *.tar

echo "Complete download and unzip packages in [$1] requirements to [$2]"