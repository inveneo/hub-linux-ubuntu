from selenium import selenium
import unittest

class TestConfigurationServer(unittest.TestCase):
    def setUp(self):
        self.selenium = selenium("localhost", \
            4444, "*firefox", "http://localhost:8008")
        self.selenium.start()
        self.selenium.open("/admin/config_remove/000000000000")
        
    def test_index_should_redirect_to_admin_dashboard(self):
        sel = self.selenium
        sel.open("/")  
        sel.wait_for_page_to_load(2500)
        self.assertTrue(sel.get_location().endswith("/admin/dashboard"))
        
    def test_click_list_configurations_shows_list_site(self):
    	sel = self.selenium
        sel.open("/admin/dashboard")
        sel.click("//input[@value='List Configurations']")
        sel.wait_for_page_to_load("30000")
    	
    def test_should_create_new_configuration(self):
    	sel = self.selenium
        sel.open("/admin/list")
 	sel.click("//input[@value='Create New']")
        sel.wait_for_page_to_load("30000")
        sel.type("mac", "000000000000")
        sel.type("timezone", "Pacific/Los Angeles")
        sel.click("ntp_on")
        sel.type("ntp_servers", "some")
        sel.click("proxy_on")
        sel.type("http_proxy", "http proxy")
        sel.type("http_proxy_port", "8080")
        sel.type("https_proxy", "https proxy")
        sel.type("https_proxy_port", "8888")
        sel.type("ftp_proxy", "ftp proxy")
        sel.type("ftp_proxy_port", "4000")
        sel.click("phone_home_on")
        sel.type("phone_home_reg", "phone home reg")
        sel.type("phone_home_checkin", "phone home checkin")
        sel.type("locale", "en_US.UTF-8")
        sel.click("single_user_login")
        sel.click("commit")
        sel.wait_for_page_to_load("30000")
        sel.open("/admin/edit/000000000000")
        self.assertEqual("000000000000", sel.get_value("mac"))
        sel.open("/admin/config_remove/000000000000")
        
    def test_should_proof_that_mac_are_unique(self):
    	import string
    	sel = self.selenium
        sel.open("/admin/config_add")
        sel.type("mac", "000000000000")
        sel.type("locale", "en_US.UTF-8")
        sel.click("commit")
        sel.wait_for_page_to_load("30000")
        sel.open("/admin/config_add")
        sel.type("mac", "000000000000")
        sel.type("locale", "en_US.UTF-8")
        sel.click("commit")
        sel.wait_for_page_to_load("30000")
        text = sel.get_body_text()
        self.assertTrue(string.find(text,"MAC is already being used") > 0) 
        sel.open("/admin/config_remove/000000000000")

    def test_should_proof_that_mac_are_12_lowercase_hex(self):
    	import string
    	sel = self.selenium
        sel.open("/admin/config_add")
        sel.type("mac", "zzzzyyyywwww")
        sel.click("commit")
        sel.wait_for_page_to_load("30000")
        text = sel.get_body_text()
        self.assertTrue(string.find(text,"MAC address must be 12 hex lower case values, no separator") > 0) 

    def test_should_proof_that_locale_complies_to_standard(self):
    	import string
    	sel = self.selenium
        sel.open("/admin/config_add")
        sel.type("locale", "Here")
        sel.click("commit")
        sel.wait_for_page_to_load("30000")
        text = sel.get_body_text()
        self.assertTrue(string.find(text,"Must be a valid locale string. E.g. en_UK.utf-8") > 0) 

    def test_should_proof_that_locale_complies_to_standard(self):
    	import string
    	sel = self.selenium
        sel.open("/configuration/get_user_config/ralph")
        
    def test_should_proof_that_there_is_always_a_deaddeadbeef_mac(self):
    	sel = self.selenium
        sel.open("/admin/edit/deaddeadbeef")
        sel.wait_for_page_to_load("2500")
        self.assertEqual("deaddeadbeef", sel.get_value("mac"))    	    	
            
    def tearDown(self):
        self.selenium.stop()

if __name__ == "__main__":
    unittest.main()