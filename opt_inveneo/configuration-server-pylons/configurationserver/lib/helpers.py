"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to both as 'h'.
"""
from webhelpers import *

import logging
import shutil
import fcntl
import os
import formencode
from formencode import validators


def tmp_file_name(log = logging.getLogger(__name__)):
    import tempfile
    tmp = tempfile.NamedTemporaryFile('w+b', -1, '', '', 'tmp')
    tmp_file = tmp.name
    tmp.close()
    return tmp_file

def get_config_dir_station():
    return get_config_dir_for('station')

def get_config_dir_user():
    return get_config_dir_for('user')

def get_config_dir_for(category):
    return 'saved-configuration/' + category + '/'

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
    import os
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
        log.info('Aquiring lock on semaphore file:' + lock_file_path)
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

def copy_from_temp_file(dest_file_path, tmp_file_path, log = logging.getLogger(__name__)):
    try:
        lock_file_path = dest_file_path + '.lock'
        log.info('Aquiring lock on semaphore file:' + lock_file_path)
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

def validate_with_regexp(regexp, value, not_empty = False, log = logging.getLogger(__name__)):
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

    log.debug('number validation: ' + str(value) + ' min: ' + str(min) + ' max: ' + str(max))

    if ret_value and value >= min and value <= max:
        ret_value = True
    else:
        ret_value = False

    log.debug(str(ret_value))

    return ret_value
        
TIMEZONES_LIST = [
['(GMT-12:00)', 'International Date Line West'],
['(GMT-11:00)', 'Midway Island, Samoa'],
['(GMT-10:00)', 'Hawaii'],
['(GMT-09:00)', 'Alaska'],
['(GMT-08:00)', 'Pacific Time (US & Canada)'],
['(GMT-08:00)', 'Tijuana, Baja California'],
['(GMT-07:00)', 'Arizona'],
['(GMT-07:00)', 'Chihuahua, La Paz, Mazatlan'],
['(GMT-07:00)', 'Mountain Time (US & Canada)'],
['(GMT-06:00)', 'Central America'],
['(GMT-06:00)', 'Central Time (US & Canada)'],
['(GMT-06:00)', 'Guadalajara, Mexico City, Monterrey'],
['(GMT-06:00)', 'Saskatchewan'],
['(GMT-05:00)', 'Bogota, Lima, Quito, Rio Branco'],
['(GMT-05:00)', 'Eastern Time (US & Canada)'],
['(GMT-05:00)', 'Indiana (East)'],
['(GMT-04:00)', 'Atlantic Time (Canada)'],
['(GMT-04:00)', 'Caracas, La Paz'],
['(GMT-04:00)', 'Manaus'],
['(GMT-04:00)', 'Santiago'],
['(GMT-03:30)', 'Newfoundland'],
['(GMT-03:00)', 'Brasilia'],
['(GMT-03:00)', 'Buenos Aires, Georgetown'],
['(GMT-03:00)', 'Greenland'],
['(GMT-03:00)', 'Montevideo'],
['(GMT-02:00)', 'Mid-Atlantic'],
['(GMT-01:00)', 'Azores'],
['(GMT-01:00)', 'Cape Verde Is.'],
['(GMT)', 'Casablanca, Monrovia, Reykjavik'],
['(GMT)', 'Greenwich Mean Time : Dublin, Edingburgh, Lisbon, London'],
['(GMT+1:00)', 'Amsterdam, Berlin, Bern, Rome, Stockholm, Vienna'],
['(GMT+1:00)', 'Belgrade, Bratislava, Budapest, Ljubljana, Prague'],
['(GMT+1:00)', 'Brussels, Copenhagen, Madrid, Paris'],
['(GMT+1:00)', 'Sarajevo, Skopje, Warsaw, Zagreb'],
['(GMT+1:00)', 'West Central Africa'],
['(GMT+2:00)', 'Amman'],
['(GMT+2:00)', 'Athens, Bucharest, Istanbul'],
['(GMT+2:00)', 'Beirut'],
['(GMT+2:00)', 'Cairo'],
['(GMT+2:00)', 'Harare, Pretoria'],
['(GMT+2:00)', 'Helsinki, Kyiv, Riga, Sofia, Tallinn, Vilnius'],
['(GMT+2:00)', 'Jerusalem'],
['(GMT+2:00)', 'Minsk'],
['(GMT+2:00)', 'Windhoek'],
['(GMT+3:00)', 'Baghdad'],
['(GMT+3:00)', 'Kuwait, Riyadh'],
['(GMT+3:00)', 'Moscov, St. Petersburg, Volograd'],
['(GMT+3:00)', 'Nairobi'],
['(GMT+3:00)', 'Tbilisi'],
['(GMT+3:30)', 'Tehran'],
['(GMT+4:00)', 'Abu Dhabi, Muscat'],
['(GMT+4:00)', 'Baku'],
['(GMT+4:00)', 'Caucasus Standard Time'],
['(GMT+4:00)', 'Yerevan'],
['(GMT+4:30)', 'Kabul'],
['(GMT+5:00)', 'Ekaterinburg'],
['(GMT+5:00)', 'Islamabad, Karachi, Tashkent'],
['(GMT+5:30)', 'Chennai, Kolkata, Mumbai, New Delhi'],
['(GMT+5:30)', 'Sri Jayawardenepura'],
['(GMT+5:45)', 'Kathmandu'],
['(GMT+6:00)', 'Almaty, Novosibirsk'],
['(GMT+6:00)', 'Astana, Dhaka'],
['(GMT+6:30)', 'Yangon (Rangoon)'],
['(GMT+7:00)', 'Bangkok, Hanoi, Jakarta'],
['(GMT+7:00)', 'Krasnoyarsk'],
['(GMT+8:00)', 'Beijing, Chongqing, Hong Kong, Urumqi'],
['(GMT+8:00)', 'Ikutsk, Ulaan Bataar'],
['(GMT+8:00)', 'Kuala Lumpur, Singapore'],
['(GMT+8:00)', 'Perth'],
['(GMT+8:00)', 'Taipei'],
['(GMT+9:00)', 'Osaka, Sapporo, Tokyo'],
['(GMT+9:00)', 'Seoul'],
['(GMT+9:00)', 'Yakutsk'],
['(GMT+9:30)', 'Adelaide'],
['(GMT+9:30)', 'Darwin'],
['(GMT+10:00)', 'Brisbane'],
['(GMT+10:00)', 'Canberra, Melbourne, Sydney'],
['(GMT+10:00)', 'Guam, Port Moresby'],
['(GMT+10:00)', 'Hobart'],
['(GMT+10:00)', 'Vladivostok'],
['(GMT+11:00)', 'Magadan, Solomon Is., New Caledonia'],
['(GMT+12:00)', 'Auckland, Wellington'],
['(GMT+12:00)', 'Fiji, Kamchatka, Marshall Is.'],
['(GMT+13:00)', 'Nuku\'alofa']
]

def get_timezones_as_string_list():
    list = []
    for tz in TIMEZONES_LIST:
        list.append(tz[0] + ' ' + tz[1])
    return list

        
LOCALES_LIST = [
'ar_DZ.UTF-8',
'ar_SA.UTF-8',
'bg_BG.UTF-8',
'zh_CN.UTF-8',
'zh_HK.UTF-8',
'zh_TW.UTF-8',
'cs_CZ.UTF-8',
'da_DK.UTF-8',
'nl_NL.UTF-8',
'en_GB.UTF-8',
'en_US.UTF-8',
'fi_FI.UTF-8',
'fr_CA.UTF-8',
'fr_FR.UTF-8',
'de_DE.UTF-8',
'el_GR.UTF-8',
'iw_IL.UTF-8',
'hu_HU.UTF-8',
'is_IS.UTF-8',
'it_IT.UTF-8',
'ja_JP.UTF-8',
'ko_KR.UTF-8',
'no_NO.UTF-8',
'pl_PL.UTF-8',
'pt_BR.UTF-8',
'pt_PT.UTF-8',
'ro_RO.UTF-8',
'ru_RU.UTF-8',
'hr_HR.UTF-8',
'sk_SK.UTF-8',
'sl_SI.UTF-8',
'es_AR.UTF-8',
'es_BO.UTF-8',
'es_CL.UTF-8',
'es_CO.UTF-8',
'es_CR.UTF-8',
'es_EC.UTF-8',
'es_SV.UTF-8',
'es_GT.UTF-8',
'es_MX.UTF-8',
'es_NI.UTF-8',
'es_PA.UTF-8',
'es_PY.UTF-8',
'es_PE.UTF-8',
'es_PR.UTF-8',
'es_ES.UTF-8',
'es_UY.UTF-8',
'es_VE.UTF-8',
'sv_SE.UTF-8',
'tr_TR.UTF-8'
]

def get_locales_as_list():
    list = []
    for l in LOCALES_LIST:
        list.append(l)
    return list

