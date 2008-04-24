# -*- coding: utf-8 -*-

FALSE_LIST=[ '', '0', 'false', 'f', 'no', 'n' ]
def is_false(val):
    return str(val).lower() in FALSE_LIST

def is_true(val):
    return not is_false(val)
