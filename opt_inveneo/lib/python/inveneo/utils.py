# -*- coding: utf-8 -*-

TRUTH_LIST=[ '1', 'true', 't', 'yes', 'y' ]
def is_true(val):
    return str(val).lower() in TRUTH_LIST
    
def is_false(val):
    return not is_true(val)
