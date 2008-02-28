#!/usr/bin/env python

import smtplib
import socket
import sys
import constants

def send_notice(subject=constants.INV_MONITOR_SMTP_DEFAULT_SUBJECT, message=constants.INV_MONITOR_SMTP_DEFAULT_MESSAGE + " " + 
socket.gethostname()):
	if constants.INV_MONITOR_SMTP_RECIPIENT == '':
		print 'unable to send message, please set recipient email'
		sys.exit(1)
	message = subject + "\n\n" + message
	try:
		s = smtplib.SMTP(constants.INV_MONITOR_SMTP_HOSTNAME, constants.INV_MONITOR_SMTP_PORT)
		s.set_debuglevel(1)
		s.ehlo()
		s.starttls()
		s.ehlo()
		s.login(constants.INV_MONITOR_SMTP_USERNAME, constants.INV_MONITOR_SMTP_PASSWORD)
		s.sendmail(constants.INV_MONITOR_SMTP_SENDER, constants.INV_MONITOR_SMTP_RECIPIENT, message)
		s.noop()
		s.rset()
		s.quit()
		s.close()
	except Exception, e:
		print "unable to send message"

if __name__ == '__main__':
	if len(sys.argv) == 1:
		send_notice()
	if len(sys.argv) > 1:	
		send_notice(sys.argv[1], sys.argv[2])
	sys.exit()

