from configurationserver.tests import *

class TestBasicController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='basic'))
        # Test response...
