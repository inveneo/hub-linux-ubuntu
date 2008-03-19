#!/usr/bin/env python
import sys
import string
sys.path.append('/opt/inveneo/lib/python/inveneo')
import fileutils, raidutils, diskutils, constants

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

def main():
        config=fileutils.ConfigFileDict(constants.INV_RAID_MONITOR_CONFIG_FILE)
        
        # assume everything is in working order
        summary_msg = "All drives are working."

        # capture the current status of the drives
        num_expected = config.get_as_int('MONITOR_EXPECTED_NUM_DRIVES')
        active_drives = raidutils.num_active_drives_in_array()
        working_drives = raidutils.num_working_drives_in_array()
        drives_in_array = raidutils.drives_in_array()
        missing_drives = raidutils.get_missing_drives_for_array(config)

        if working_drives < num_expected:
                drive_str = "drives" if working_drives>1 else "drive" 
                summary_msg = "Only %d %s out of %d were found." % (working_drives, drive_str, num_expected)
        
        # build a list of tuples for all drives with the following information:
        # ( drive_num, logical name, serial number, drive state[missing, active, fautly, spare] )
        # for missing drives the logical name will be empty
        all_drive_information = [] 

        for logical_name,drive_state in drives_in_array:
                serial_num=diskutils.id_for_device('/dev/%s' % logical_name)
                serial_num='def456'
                drive_num=get_drive_number(config,serial_num,num_expected)
                all_drive_information.append( (drive_num, logical_name, serial_num, drive_state) )

        for drive_num,serial_num in missing_drives:
                logical_name='Not Connected'
                drive_state='missing'
                all_drive_information.append( (drive_num, logical_name, serial_num, drive_state) )
        
        all_drive_information.sort(lambda x,y: cmp(x[0],y[0]))
        
        #output the html
        print "<table cellspacing=10><tr>"
        for drive_num, logical_name, serial_num, drive_state in all_drive_information:
                if drive_state == 'missing' or drive_state == 'faulty': 
                    print "<td><table><tr><td>Drive Number: %d</td></tr><tr><td>Logical Name: %s</td></tr><tr><td>Serial: %s</td></tr><tr><td>State: <font color='red'>%s</font></td></tr></table></td>" % (drive_num, logical_name, serial_num, drive_state)
                else:
                    print "<td><table><tr><td>Drive Number: %d</td></tr><tr><td>Logical Name: %s</td></tr><tr><td>Serial: %s</td></tr><tr><td>State: %s</td></tr></table></td>" % (drive_num, logical_name, serial_num, drive_state)
        print "</tr></table>"

if __name__ == "__main__":
        main()
