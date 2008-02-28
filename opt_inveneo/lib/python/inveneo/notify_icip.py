import smtplib
import socket
import sys
SMTP_USERNAME='inveneo.smtp@gmail.com'
SMTP_PASSWORD='1qaz2wsx'
SMTP_HOSTNAME='smtp.gmail.com'
SMTP_PORT=587
SMTP_TLS=1
SMTP_SENDER='inveneo.smtp@gmail.com'
SMTP_RECIPIENT='sammy.zahabi@gmail.com' #icip address
SMTP_DEFAULT_MESSAGE="Host has a failed disk drive:"
SMTP_DEFAULT_SUBJECT="Subject: Disk failed"
def send_notice(subject=SMTP_DEFAULT_SUBJECT, message=SMTP_DEFAULT_MESSAGE + " " + 
socket.gethostname()):
#	message = SMTP_DEFAULT_MESSAGE + str(socket.gethostname)
# get the email message from a file
	message = subject + "\n\n" + message
	try:
		s = smtplib.SMTP(SMTP_HOSTNAME, SMTP_PORT)
		s.set_debuglevel(1)
		s.ehlo()
		s.starttls()
		s.ehlo()
		s.login(SMTP_USERNAME, SMTP_PASSWORD)
		s.sendmail(SMTP_SENDER, SMTP_RECIPIENT, message)
		s.noop()
		s.rset()
		s.quit()
		s.close()
	except Exception, e:
		print "network down"

if __name__ == '__main__':
	if len(sys.argv) == 1:
		send_notice()
	if len(sys.argv) > 1:	
		send_notice(sys.argv[1], sys.argv[2])
	sys.exit()

