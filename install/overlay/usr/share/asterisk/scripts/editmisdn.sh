#!/bin/bash

####################################################################
####	Copyright Brandon Kruse <bkruse@digium.com> && Digium	####
####################################################################

# Quick script for applying misdn settings from the GUI.

MISDNCONF="/etc/misdn-init.conf"
MISDNFILE="/etc/asterisk/applymisdn.conf"
grep -v "\[general\]" ${MISDNFILE} | grep -v "\;" > ${MISDNCONF}
