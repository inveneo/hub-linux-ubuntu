"""The application's Globals object"""

"""
Please refer to:
    http://svn.inveneo.org/browse/wsvn/inveneo-linux-ubuntu/trunk/opt_inveneo/lib/python/inveneo/config.py
"""

from pylons import config

class Globals(object):
    """Globals acts as a container for objects available throughout the
    life of the application
    """
    # globals Ralph had in the base.py class
    DEFAULT_DYN_ATTRS={
        'INV_CONFIG_HOST': 'set me',
        'INV_CONFIG_HOST_TYPE': 'set me',
        'INV_HOSTNAME': 'set me',
    }

    DEFAULT_DB_ATTRS={
        'INV_LANG': "en_US.UTF-8",
        'INV_TIME_ZONE': "America/Los_Angeles",

        'INV_CONFIG_HOST': "raw-partitioned",
        'INV_CONFIG_HOST_TYPE': "station",

        'INV_PROXY_ON': False,

        'INV_NTP_ON': True,
        'INV_NTP_SERVERS': "hub.local:pool.ntp.org:ntp.ubuntu.com",

        'INV_LOCAL_USER_DOCS_DIR_ON': False,
        'INV_LOCAL_SHARED_DOCS_DIR_ON': False,
        'INV_HUB_DOCS_DIRS_ON': True,

        'INV_PHONE_HOME_ON': False,
        'INV_PHONE_HOME_REG_URL': "http://community.inveneo.org/phonehome/reg",
        'INV_PHONE_HOME_CHECKIN_URL': \
                "http://community.inveneo.org/phonehome/checkin"
        }

    NONE = 'None'
    NOT_FOUND = 'not found'
    NONE_TYPE = "<type 'NoneType'>"
    BUFF_SIZE = 1024
    MAC_REGEXP = '^[0-9a-f]{12,12}$'
    LANG_REGEXP = '^[a-z][a-z](_[A-Z][A-Z](.[uU][tT][fF]-8)?)?$'

    # globals Ralph had in the helpers.py class
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

    LANGS_LIST = [
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

    # jwiggins additions
    STATION = 'station'
    USER = 'user'
    TEMP_DIR = '/opt/inveneo/config-server/tmp'
    SAVE_DIR = '/opt/inveneo/config-server/saved-configuration'
    SWEEP_SECS = 180
    HOST_TYPES = ['station', 'hub']

    DEFAULT_ADMIN = 'inveneo'
    DEFAULT_SERVER = 'inveneo-hub'
    DEFAULT_STATION = 'inveneo-station'
    DEFAULT_MAC = 'ffffffffffff'
    FACTORY_CONFIG = 'blank.tar.gz'

    def __init__(self):
        """One instance of Globals is created during application
        initialization and is available during requests via the 'g'
        variable
        """
        pass
