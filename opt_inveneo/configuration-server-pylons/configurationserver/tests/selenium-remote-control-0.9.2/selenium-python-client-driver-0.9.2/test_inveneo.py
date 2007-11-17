from selenium import selenium
import unittest
import os
import string
import httplib
import time

PROTOCOL = "http"
URL = "192.168.1.104"
PORT = "8008"

class TestConfigurationServer(unittest.TestCase):
    def assertStringInBodyText(self, str_txt):
    	self.assertTrue(string.find(self.selenium.get_body_text(), str_txt) >= 0)

    def setUp(self):
        self.selenium = selenium("localhost", \
            4444, "*firefox", PROTOCOL + "://" + URL + ":" + PORT)
        self.selenium.start()
        self.selenium.open("/signin/signin")
	self.selenium.type("username", "Inveneo")
	self.selenium.type("password", "1nvene0")
	self.selenium.click("commit")
        self.selenium.wait_for_page_to_load("30000")
        self.selenium.open("/admin/config_remove/000000000000")        	
        self.selenium.open("/admin/station_remove/111111111111")
        
    def test_wrong_loging_should_show_error_message(self):
       	sel = self.selenium
        sel.open("/signin/signin")
	sel.type("username", "wrong")
	sel.type("password", "worse")
	sel.click("commit")
        sel.wait_for_page_to_load("30000")
        self.assertStringInBodyText("Username and password combination are not valid.")
        
    def test_signout_should_redirect_to_signin_and_stay(self):
       	sel = self.selenium
	sel.open("/admin/dashboard")
        sel.click("link=Signout")
        sel.wait_for_page_to_load("30000")
        self.assertTrue(string.find(sel.get_location(), "/signin/signout") >= 0)
	sel.open("/admin/dashboard")
        sel.wait_for_page_to_load("30000")
        self.assertTrue(string.find(sel.get_location(), "/signin/signin") >= 0)
        
    def test_up_and_download_station_config(self):
        sel = self.selenium
        sel.open("/admin/set_server_on/1?on=True")
        sel.wait_for_page_to_load("30000")
    	os.system('curl --fail -s -w %{size_upload} -F config_file=@def_station_config.tar.gz http://' + URL + ':' + PORT + '/configuration/save_station_config/111111111111 -v')
        sel.click("//input[@value='List Station Configurations']")
        sel.wait_for_page_to_load("30000")
        self.assertStringInBodyText("111111111111")        
        os.system('curl -O http://' + URL + ':' + PORT + '/configuration/get_station_config/111111111111')
	self.assertEquals(os.stat('def_station_config.tar.gz')[6], os.stat('111111111111')[6])
	os.remove('111111111111')
        
    def test_get_501_on_get_config_when_server_is_off(self):   	
       	sel = self.selenium
	sel.open("/admin/dashboard")
	sel.wait_for_page_to_load("2500")
	text = sel.get_body_text()
	if (string.find(text, "YES") > 0):
	    sel.click("//input[@value='Toggle']")
	    sel.wait_for_page_to_load("30000")
    	conn = httplib.HTTPConnection(URL + ":" + PORT)
    	conn.request("GET", "/configuration/get_user_config/any_name_will_do")
    	req = conn.getresponse()
    	conn.close()
    	self.assertEquals(501, req.status)
    	conn.request("GET", "/configuration/get_station_config/any_mac_will_do")
	req = conn.getresponse()
	conn.close()
	self.assertEquals(501, req.status)
    	conn.request("GET", "/configuration/get_station_initial_config/any_mac_will_do")
	req = conn.getresponse()
	conn.close()
	self.assertEquals(501, req.status)
	
	sel.open("/admin/dashboard")
	sel.wait_for_page_to_load("2500")
	text = sel.get_body_text()
	if (string.find(text, "NO") > 0):
	    sel.click("//input[@value='Toggle']")
        
    def test_get_404_on_save_config_when_server_is_off(self):   	
       	sel = self.selenium
	sel.open("/admin/dashboard")
	sel.wait_for_page_to_load("2500")
	text = sel.get_body_text()
	if (string.find(text, "YES") > 0):
	    sel.click("//input[@value='Toggle']")
	    sel.wait_for_page_to_load("30000")
    	conn = httplib.HTTPConnection(URL + ":" + PORT)
    	conn.request("GET", "/configuration/save_user_config/any_name_will_do")
    	req = conn.getresponse()
    	conn.close()
    	self.assertEquals(404, req.status)
    	conn.request("GET", "/configuration/save_station_config/any_mac_will_do")
	req = conn.getresponse()
	conn.close()
	self.assertEquals(404, req.status)
    	conn.request("GET", "/configuration/save_station_initial_config/any_mac_will_do")
	req = conn.getresponse()
	conn.close()
	self.assertEquals(404, req.status)
	
	sel.open("/admin/dashboard")
	sel.wait_for_page_to_load("2500")
	text = sel.get_body_text()
	if (string.find(text, "NO") > 0):
	    sel.click("//input[@value='Toggle']")

    def test_index_should_redirect_to_admin_dashboard(self):
        sel = self.selenium
        sel.open("/")  
        sel.wait_for_page_to_load(30000)
	time.sleep(2)        
        location = sel.get_location()
        self.assertTrue(string.find(location, "/admin/dashboard") >= 0)
        
    def test_click_list_configurations_shows_list_site(self):
    	sel = self.selenium
        sel.open("/admin/dashboard")
        sel.click("//input[@value='List Initial Configurations']")
        sel.wait_for_page_to_load("30000")
    	
    def test_should_create_new_configuration(self):
    	sel = self.selenium
        sel.open("/admin/list_initial_configurations")
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
        self.assertStringInBodyText("000000000000")
        sel.open("/admin/config_remove/000000000000")
        
    def test_should_proof_that_mac_are_unique(self):
    	sel = self.selenium
        sel.open("/admin/config_add")
        sel.type("mac", "000000000000")
        sel.type("http_proxy_port", "8080")
        sel.type("https_proxy_port", "8888")
        sel.type("ftp_proxy_port", "4000")
        sel.type("locale", "en_US.UTF-8")
        sel.click("commit")
        sel.wait_for_page_to_load("30000")
        sel.open("/admin/config_add")
        sel.type("mac", "000000000000")
        sel.type("http_proxy_port", "8080")
        sel.type("https_proxy_port", "8888")
        sel.type("ftp_proxy_port", "4000")
        sel.type("locale", "en_US.UTF-8")
        sel.click("commit")
        sel.wait_for_page_to_load("30000")
        self.assertStringInBodyText("MAC is already being used")
        sel.open("/admin/config_remove/000000000000")

    def test_should_proof_that_mac_are_12_lowercase_hex(self):
    	sel = self.selenium
        sel.open("/admin/config_add")
        sel.type("mac", "zzzzyyyywwww")
        sel.click("commit")
        sel.wait_for_page_to_load("30000")
        self.assertStringInBodyText("MAC address must be 12 hex lower case values, no separator")

# right now locale comes from a combo box
#
#    def test_should_proof_that_locale_complies_to_standard(self):
#    	sel = self.selenium
#        sel.open("/admin/config_add")
#        sel.type("locale", "Here")
#        sel.click("commit")
#        sel.wait_for_page_to_load("30000")
#        text = sel.get_body_text()
#        self.assertTrue(string.find(text,"Must be a valid locale string. E.g. en_UK.utf-8") > 0) 

    def test_switch_server_on_off(self):
    	sel = self.selenium
        sel.open("/admin/set_server_on/1?on=True")
        sel.wait_for_page_to_load("30000")
        self.assertStringInBodyText("YES")
        sel.open("/admin/set_server_on/1?on=False")
        sel.wait_for_page_to_load("30000")
        self.assertStringInBodyText("NO")
        sel.open("/admin/set_server_on/1?on=True")
        sel.wait_for_page_to_load("30000")
        self.assertStringInBodyText("YES")

    def test_toggle_server_on_off(self):
    	sel = self.selenium
        sel.open("/admin/dashboard")
        sel.wait_for_page_to_load("2500")
        if string.find(sel.get_body_text(), "YES"):
            expected = "NO"
        else:
            expected = "YES"
	sel.click("//input[@value='Toggle']")
        sel.wait_for_page_to_load("30000")
	self.assertStringInBodyText(expected)     
	
    def test_swich_all_stations_on_off(self):
    	sel = self.selenium
        sel.open("/admin/dashboard?")
        sel.click("//input[@value='List Station Configurations']")
        sel.wait_for_page_to_load("30000")
        sel.click("//input[@value='All On']")
        sel.wait_for_page_to_load("30000")
        text = sel.get_body_text()
	self.assertTrue(string.find(text,"NO") == -1)      
        sel.click("//input[@value='All Off']")
        sel.wait_for_page_to_load("30000")
        text = sel.get_body_text()
	self.assertTrue(string.find(text,"YES") == -1)      
	        
    def test_should_proof_that_there_is_always_a_deaddeadbeef_mac(self):
    	sel = self.selenium
        sel.open("/admin/edit/deaddeadbeef")
        sel.wait_for_page_to_load("2500")
        self.assertStringInBodyText("deaddeadbeef")
        
    def tearDown(self):
        self.selenium.stop()

if __name__ == "__main__":
    unittest.main()
