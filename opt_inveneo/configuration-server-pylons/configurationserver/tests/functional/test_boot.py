from configurationserver.tests import *

class TestBootController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='boot'))
        # Test response...
