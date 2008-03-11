# -*- coding: utf-8 -*-

import sys
import os
import subprocess as sp
sys.path.append('/opt/inveneo/lib/python')
from inveneo import raidstatus

class RaidStatusHandler:
    def __init__(self):
	pass

    def num_drives_in_mirror(self):
	return raidstatus.num_drives_in_mirror()

    def updateCurrentStatus(self):
        raidstatus.update_status()

class RaidNotificationDecider:
    def isThisAnError(self,message,numDrives):
        if (message == "SpareActive" or message == "RebuildFinished"):
            return False
        else:
            return (message == "Fail" or message == "DegradedArray") and numDrives == 2

    def shouldChangeStateInformation(self,message,numDrives):
        return (message == "SpareActive" or message == "RebuildFinished") and numDrives == 1

class RaidNotifier:
    def sound_audio_alert():
        sp.call(constants.INV_MONITOR_BEEP_ALERT.split())
        
    def send_email_notice(subject=constants.INV_MONITOR_SMTP_DEFAULT_SUBJECT, \
                    message=constants.INV_MONITOR_SMTP_DEFAULT_MESSAGE + " " + socket.gethostname()):
        
        syslog.openlog('inv-notify-icip', 0, syslog.LOG_LOCAL5)

        '''
        for key in os.environ.keys():
            line = key + "=" + os.environ[key]
            syslog.syslog(line)
            print line
        '''

        if constants.INV_MONITOR_SMTP_RECIPIENT == '':
            syslog.syslog("Recipient email not set. Exiting.")
            print 'unable to send message, please set recipient email'
            sys.exit(1)

        message = subject + "\n\n" + message
        try:
            syslog.syslog("Opening SMTP connection")
            s = smtplib.SMTP(constants.INV_MONITOR_SMTP_HOSTNAME, constants.INV_MONITOR_SMTP_PORT)
            # s.set_debuglevel(1)
            s.ehlo()
            s.starttls()
            s.ehlo()
            s.login(constants.INV_MONITOR_SMTP_USERNAME, constants.INV_MONITOR_SMTP_PASSWORD)
            s.sendmail(constants.INV_MONITOR_SMTP_SENDER, constants.INV_MONITOR_SMTP_RECIPIENT, message)
            s.noop()
            s.rset()
            s.quit()
            s.close()
            syslog.syslog("Closed SMTP connection")
	except Exception, e:
            syslog.syslog("Unable to send message. Exception: " + e.message)
            sys.stderror.write("Unable to send message: " + e.message)


        
