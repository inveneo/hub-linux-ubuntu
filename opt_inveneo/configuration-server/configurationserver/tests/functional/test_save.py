from configurationserver.tests import *

class TestSaveController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='save'))
        # Test response...
