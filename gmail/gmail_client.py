import smtplib
import logging
import ssl

logger = logging.getLogger(__name__)


class GmailClient:
	username = ""
	password = ""
	sent_from = ""
	context = ssl.create_default_context()

	def __init__(self, sender, username, password):
		self.username = username
		self.password = password
		self.sent_from = sender

	def send(self, address, title, text):
		message = """From: %s\nTo: %s\nSubject: %s\n\n%s""" % (self.sent_from, ", ".join(address), title, text)
		try:
			server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
			server.ehlo()
			server.login(self.username, self.password)
			server.sendmail(self.sent_from, address, message)
			server.quit()
			server.close()
		except Exception as ex:
			logger.exception('Error sending Gmail message')

if __name__ == "__main__":

	gmail_client = GmailClient("koldaman@gmail.com", "username", "password")
	push = gmail_client.send(['koldaman@gmail.com', 'info@e23.cz'], "This is the title", "This is the body")
	print push

