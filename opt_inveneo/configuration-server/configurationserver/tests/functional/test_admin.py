from configurationserver.tests import *

class TestAdminController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='admin'))
        # Test response...
