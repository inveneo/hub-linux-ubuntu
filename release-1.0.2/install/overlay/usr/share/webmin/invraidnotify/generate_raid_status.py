#!/usr/bin/env python
import sys
import string
from inveneo import fileutils, raidutils, diskutils, constants

def get_drive_number(config,serial_num,num_expected_drives):
        if serial_num == None: 
                return -1 

        for drive_num in range(num_expected_drives+1):
                config_serial = config.get_as_str("DISK%d" % drive_num)
                if not config_serial:
                        continue
                elif config_serial.lower().strip() == serial_num.lower().strip():
                        return drive_num
        return -1

def get_drive_info_for_array(config,raid_dev):
        # capture the current status of the drives
        num_expected = config.get_as_int('MONITOR_EXPECTED_NUM_DRIVES')
        working_drives = raidutils.num_working_drives_in_array(raid_dev)
        drives_in_array = raidutils.drives_in_array(raid_dev)
        missing_drives = raidutils.get_missing_drives_for_array(config,raid_dev)

        # build a list of tuples for all drives with the following information:
        # ( drive_num, logical name, serial number, drive state[missing, active, fautly, spare] )
        # for missing drives the logical name will be empty
        all_drive_information = [] 

        for logical_name,drive_state in drives_in_array:
                serial_num=diskutils.id_for_device('/dev/%s' % logical_name)
                
                if serial_num==None:
                        serial_num=None
                        drive_num=-1
                else:
                        drive_num=get_drive_number(config,serial_num,num_expected)
                all_drive_information.append( (drive_num, logical_name, serial_num, drive_state) )

        for drive_num,serial_num in missing_drives:
                logical_name='None'
                drive_state='missing'
                all_drive_information.append( (drive_num, logical_name, serial_num, drive_state) )

        all_drive_information.sort(lambda x,y: cmp(x[0],y[0]))

        return [raid_dev,all_drive_information];

def print_header_information(all_array_drive_info): 
        print "<tr><td class='header'>&nbsp;</td>"
        array1_drive_info = all_array_drive_info[0][1]
        x=1
        for drive_num, logical_name, serial_num, drive_state in array1_drive_info:
                print "<td class='header'>Drive: %d<br>Serial: %s</td>" % (x, serial_num) 
                x=x+1
        print "</tr>"                

def print_array_information(all_array_drive_info):
        for array_name, array_drives in all_array_drive_info:
            print "<tr>"
            print "<td class='header'>Array: %s</td>" % array_name
            for drive_num, logical_name, serial_num, drive_state in array_drives:
                print "<td class='%s'>Name: %s<br>Status: %s</td>" % (drive_state, logical_name, drive_state)
            print "</tr>"

def print_css_definitions():
        print "<style type='text/css'>"
        print ".header { background-color: #cccccc; }"
        print ".active { background-color: #1fd40c; }"
        print ".missing { background-color: #f11020; }"
        print ".faulty { background-color: #f11020; }"
        print ".spare{ background-color: #e6e835; }"
        print "</style>"

def print_drive_info(config,raid_arrays):
        num_arrays = len(raid_arrays)
        all_array_drive_info = [ get_drive_info_for_array(config,array) for array in raid_arrays ]
        
        print_css_definitions()
        print "<table cellpadding='4' cellspacing='0' border='1'>"
        print_header_information(all_array_drive_info)
        print_array_information(all_array_drive_info)
        print "</table>"

def main():
        config=fileutils.ConfigFileDict(constants.INV_RAID_MONITOR_CONFIG_FILE)
        raid_arrays = ['/dev/md0','/dev/md1','/dev/md2']
        print_drive_info(config,raid_arrays)

if __name__ == "__main__":
        main()
