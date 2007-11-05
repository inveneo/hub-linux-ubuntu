"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to both as 'h'.
"""
from webhelpers import *

import logging

def tmp_file_name(log = logging.getLogger(__name__)):
    import tempfile
    tmp = tempfile.NamedTemporaryFile('w+b', -1, '', '', 'tmp')
    tmp_file = tmp.name
    tmp.close()
    return tmp_file

def does_parameter_exist(request, name, log = logging.getLogger(__name__)):
    if not name in request.params.keys():
        log.error('Parameter is not set: ' + name)
        return False
    else:
        log.info('Parameter is set: ' + name)
        return True

def does_file_exist(file_path, log = logging.getLogger(__name__)):
    import os
    if not os.path.exists(file_path):
        log.error('File not existing: ' + file_path)
        return False
    else:
        log.info('File existing: ' + file_path)
        return True
        
def copy_to_temp_file(source_file_path, log = logging.getLogger(__name__)):
    import shutil
    import fcntl
    import os
    tmp_file = tmp_file_name()         
    try:
        log.info('Aquiring lock on semaphore file')
        lock_file_path = source_file_path + '.lock'
        lock_file = open(lock_file_path, 'a+')
        fcntl.lockf(lock_file, fcntl.LOCK_EX)
        log.info('Copying file')
        shutil.copyfile(source_file_path, tmp_file)
    finally:
        log.info('Cleaning up -- removing lock file')
        fcntl.lockf(lock_file, fcntl.LOCK_UN)
        lock_file.close()
        os.remove(lock_file_path)
        return tmp_file

def is_checkbox_set(request, name, log = logging.getLogger(__name__)):
    if not name in request.params.keys():
        log.info('Checkbox is not set: ' + name)
        return False;
    else:
        log.info('Checkbox is set: ' + name)
        return True;
