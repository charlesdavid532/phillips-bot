import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import os

class Email(object):
	"""Class for sending Email. There are 2 types of smtp servers used gmail and sparkpost"""
	def __init__(self, fromAddr, toAddr, subject, body, attachment):
		super(Email, self).__init__()
		self.fromAddr = fromAddr
		self.toAddr = toAddr
		self.subject = subject
		self.body = body

		if attachment != None and attachment != "":
			self.hasAttachment = True
			self.attachmentName = attachment["attachmentName"]
			self.attachmentBody = attachment["attachmentBody"]
		
		#Defining the default smtp server
		self.smtpServer = "gmail"



	def sendEmail(self):
		if self.smtpServer == "gmail":
			self.sendGoogleEmail()
		else:
			self.sendSparkPostEmail()


	def sendGoogleEmail(self):
		msg = MIMEMultipart()
		msg['From'] = self.fromAddr
		msg['To'] = self.toAddr
		msg['Subject'] = self.subject
		 
		body = self.body
		msg.attach(MIMEText(body, 'plain'))
		 
		server = smtplib.SMTP('smtp.gmail.com', 587)
		server.starttls()
		server.login(fromaddr, os.environ['GMAIL_SECRET'])
		text = msg.as_string()
		server.sendmail(self.fromAddr, self.toAddr, text)
		server.quit()


	def sendSparkPostEmail(self):
		print("Should send a email via spark")
