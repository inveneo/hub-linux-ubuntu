#!/bin/bash

####################################################################
####	Copyright Brandon Kruse <bkruse@digium.com> && Digium	####
####################################################################

# Quick script for applying zaptel settings from the GUI.

ZAPCONF="/etc/zaptel.conf"
FILENAME="/etc/asterisk/applyzap.conf"
grep -v '\;' ${FILENAME} | sed 's/\[general\]//g' > ${ZAPCONF}

