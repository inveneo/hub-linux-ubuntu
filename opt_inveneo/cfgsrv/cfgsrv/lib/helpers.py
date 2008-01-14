"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to both as 'h'.
"""
from webhelpers import *
from pylons import g
import logging, tempfile, os, fcntl, shutil
from formencode import validators

def is_default_initial_config(config):
    if config.mac == g.DEFAULT_MAC:
        return True
    else:
        return False

def tmp_file_name(log = logging.getLogger(__name__)):
    tmp = tempfile.NamedTemporaryFile('w+b', -1, '', '', g.TEMP_DIR)
    tmp_file = tmp.name
    tmp.close()
    return tmp_file

def get_config_dir_station():
    return get_config_dir_for(g.STATION)

def get_config_dir_user():
    return get_config_dir_for(g.USER)

def get_config_dir_for(category):
    return g.SAVE_DIR + '/' + category + '/'

def toggle_boolean(flag):
    return not bool(flag)

def does_parameter_exist(request, name, log = logging.getLogger(__name__)):
    if not name in request.params.keys():
        log.error('Parameter is NOT set: ' + name)
        return False
    else:
        log.info('Parameter IS set: ' + name)
        return True

def does_file_exist(file_path, log = logging.getLogger(__name__)):
    if not os.path.exists(file_path):
        log.error('File not existing: ' + file_path)
        return False
    else:
        log.info('File existing: ' + file_path)
        return True

def copy_to_temp_file(source_file_path, log = logging.getLogger(__name__)):
    tmp_file = tmp_file_name()
    try:
        lock_file_path = source_file_path + '.lock'
        log.info('Aquiring lock on semaphore file: ' + lock_file_path)
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

def copy_from_temp_file(dest_file_path, tmp_file_path,
        log = logging.getLogger(__name__)):
    try:
        lock_file_path = dest_file_path + '.lock'
        log.info('Aquiring lock on semaphore file: ' + lock_file_path)
        lock_file = open(lock_file_path, 'a+')
        fcntl.lockf(lock_file, fcntl.LOCK_EX)
        log.info('Copying file')
        shutil.copyfile(tmp_file_path, dest_file_path)
    finally:
        log.info('Cleaning up -- removing lock file')
        fcntl.lockf(lock_file, fcntl.LOCK_UN)
        lock_file.close()
        os.remove(lock_file_path)

def is_checkbox_set(request, name, log = logging.getLogger(__name__)):
    if not name in request.params.keys():
        log.info('Checkbox is not set: ' + name)
        return False;
    else:
        log.info('Checkbox is set: ' + name)
        return True;

def escape_quotes(string):
    return str(string).replace(r'"', r'\"')

def validate_with_regexp(regexp, value, not_empty = False,
        log = logging.getLogger(__name__)):
    value = str(value)

    log.debug('regexp validation: ' + str(regexp) + ' ~= ' + value)

    ret_value = True

    if (not_empty) and (len(value) == 0):
        ret_value = False

    re = validators.Regex(regex = regexp)
    try:
        re.to_python(value)
    except:
        ret_value = False

    log.debug(str(ret_value))

    return ret_value

def validate_number(min, max, value, log = logging.getLogger(__name__)):

    ret_value = True

    try:
        value = int(value)
        min = int(min)
        max = int(max)
    except:
        ret_value = False

    log.debug('number validation: ' + str(value) + ' min: ' + str(min) + \
            ' max: ' + str(max))

    if ret_value and value >= min and value <= max:
        ret_value = True
    else:
        ret_value = False

    log.debug(str(ret_value))

    return ret_value

def get_timezones_as_string_list():
    list = []
    for tz in g.TIMEZONES_LIST:
        list.append(tz[0] + ' ' + tz[1])
    return list

def get_locales_as_list():
    list = []
    for l in g.LOCALES_LIST:
        list.append(l)
        return list