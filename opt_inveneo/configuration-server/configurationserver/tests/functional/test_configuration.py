from configurationserver.tests import *

class TestConfigurationController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='configuration'))
        # Test response...
