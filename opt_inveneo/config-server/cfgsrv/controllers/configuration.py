import logging
import paste
import socket
import os
import os.path

from cfgsrv.lib.base import *
from cfgsrv.controllers.authentication import *

log = logging.getLogger(__name__)

class ConfigurationController(BaseController):
    """Controller to handle HTTP requests from client machines"""

    def _return_config_file(self, name, category):
        log.debug('_return_config_file(%s, %s)' % (name, category))
        if not name or not category:
            abort(404, 'Need a valid user name and category')
        config_file_path = os.path.join(g.SAVE_DIR, category, name + '.tar.gz')
        if not os.path.exists(config_file_path):
            abort(404, 'Config file not found')
        tmp_config_file = h.copy_to_temp_file(config_file_path, log)
        if not tmp_config_file:
            abort(404, 'No config file found')
        fapp = paste.fileapp.FileApp(tmp_config_file)
        return fapp(request.environ, self.start_response)

    def _save_config_file(self, request, name, category):
        # curl --fail -s -w %{size_upload} -F config_file=@<file> \
        # http://localhost:8008/configuration/save_user_config/<name> -v
        log.debug('_save_config_file(%s, %s)' % (name, category))
        if not name or not category:
            abort(404, 'Need a valid user name and category')
        if not request.params.has_key('config_file'):
            abort(400, 'No config file sent')
        config_file = request.POST['config_file']
        tmp_dest_file = h.tmp_file_name(log)
        if config_file.file:
            out = open(tmp_dest_file, "w+")
            while 1:
                byte = config_file.file.read(g.BUFF_SIZE)
                if not byte: break
                out.write(byte)
            out.close()
        dstfile = os.path.join(h.get_config_dir_for(category), name + '.tar.gz')
        result = h.copy_from_temp_file(dstfile, tmp_dest_file)
        os.remove(tmp_dest_file)
        return result

    def _is_server_on(self):
        log.debug('_is_server_on()')
        servers = model.Session.query(model.Server)
        server = servers.filter(model.Server.name == g.DEFAULT_SERVER).one()
        return server.server_on

    def _is_station_on(self, mac):
        log.debug('_is_station_on(%s)' % mac)
        stations = model.Session.query(model.Station)
        station = stations.filter(model.Station.mac == mac).first()
        if station:
            return station.on
        else:
            return False

    ###########################
    # controller methods
    ###########################    
    def index(self):
        return

    def get_user_config(self, id):
        log.debug("get_user_config(%s)" % id)
        if not self._is_server_on():
            abort(501, 'Server is not on')
        return self._return_config_file(id, 'user')

    def get_station_config(self, id):
        log.debug("get_station_config(%s)" % id)
        if not self._is_server_on():
            abort(501, 'Server is not on')
        if not self._is_station_on(id):
            abort(404, 'Station is not on')
        # XXX for now, we force everything into default MAC
        id = g.DEFAULT_MAC
        return self._return_config_file(id, 'station')

    def get_station_initial_config(self, id):
        log.debug("get_station_initial_config(%s)" % id)
        if not self._is_server_on():
            abort(501, 'Server is not on')

        # XXX for now, we force everything into default MAC
        #mac = id 
        mac = g.DEFAULT_MAC

        stations = model.Session.query(model.Station)
        station = stations.filter(model.Station.mac == mac).first()
        if not station:
            abort(404, 'No initial config for station')

        # write a temp properties file to be returned as response
        tmp_file_path = h.tmp_file_name(log)
        output = open(tmp_file_path, 'a+')
        proplist = ['#Initial Configuration\n']
        for key, value in station.properties().iteritems():
            line = '%s="%s"\n' % (key, h.escape_quotes(value))
            proplist.append(line)
        output.writelines(proplist)
        output.close()

        # return response XXX how to remove temp file?
        fapp = paste.fileapp.FileApp(tmp_file_path)
        return fapp(request.environ, self.start_response)

    def save_user_config(self, id):
        log.debug("save_user_config(%s)" % id)
        if not self._is_server_on():
            abort(503, 'Server Not On')
        response.status_code = self._save_config_file(request, id, 'user')

    def save_station_config(self, id):
        log.debug("save_station_config(%s)" % id)
        if not self._is_server_on():
            abort(503, 'Server Not On')
        # XXX for now, we force everything into default MAC
        id = g.DEFAULT_MAC
        response.status_code = self._save_config_file(request, id, 'station')

    def save_station_initial_config(self, id):
        log.debug("save_station_initial_config(%s)" % id)
        if not self._is_server_on():
            abort(503, 'Server Not On')
        if not request.params.has_key('config_file'):
            log.error('No config file found')
            abort(400, 'No config file found')

        # XXX for now, we force everything into default MAC
        #mac = id 
        mac = g.DEFAULT_MAC

        # create dictionary of sent values
        # XXX should use xml.sax.saxutils or urllib to do this!
        config_file = request.POST['config_file']
        items = {}
        if config_file.file:
            while 1:
                line = config_file.file.readline()
                if not line: break        
                elems = line.split("=")
                if len(elems) == 2:
                    key = elems[0].strip()
                    value = elems[1].strip().strip('"')
                    items[key] = value

        # update/add to DB
        stations = model.Session.query(model.Station)
        station = stations.filter(model.Station.mac == mac).first()
        if not station:
            station = model.Station(mac)
            model.Session.save(station)
        station.update(items)
        model.Session.update(station)
        model.Session.commit()

    def toggle_station_on(self, mac):
        log.debug('toggle_station_on(%s)' % mac)
        q = model.Session.query(model.Station)
        r = q.filter(model.Station.mac == mac).first()
        if r:
            r.on = not r.on
            model.Session.save(r)
            model.Session.commit()
        else:
            log.debug('station %s not found!' % mac)
        redirect_to('/admin/list_station_configurations')

    def set_all_stations_on(self):
        log.debug('set_all_stations_on(%s)' % mac)
        on_off = request.params['all_on']
        q = model.Session.query(model.Station)
        for r in q.all():
            r.on = True
            model.Session.save(r)
        model.Session.commit()
        redirect_to('/admin/list_station_configurations')

