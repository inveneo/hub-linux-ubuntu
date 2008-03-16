#!/bin/bash
if [ $# -lt 3 ] 
then
    echo "Usage: gen_csr.sh <conf-file> <key> <csr name>"
    exit 1
fi
	
openssl req -config $1 -new -nodes -key $2 -out $3
