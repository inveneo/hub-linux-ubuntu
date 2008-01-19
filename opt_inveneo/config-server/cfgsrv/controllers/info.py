import logging
import paste
import os

from cfgsrv.lib.base import *

log = logging.getLogger(__name__)

VERSION_FILE='config-server-version.txt'

class InfoController(BaseController):
    def get_version(self):
        log.debug('get_version(): getcwd = %s' % os.getcwd())
        fapp = paste.fileapp.FileApp(VERSION_FILE)
        return fapp(request.environ, self.start_response)
