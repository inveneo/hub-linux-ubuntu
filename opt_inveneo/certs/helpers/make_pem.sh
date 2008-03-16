#!/bin/bash
if [ $# -lt 3 ] 
then
    echo "Usage: make_pem <privkey> <cert> <pem>"
    exit 1
fi
	
cat $1 $2 > $3

