import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import boto3
from botocore.client import Config

BUCKET_NAME = 'tonibot-bucket'

class Email(object):
	"""Class for sending Email. There are 2 types of smtp servers used gmail and sparkpost"""
	def __init__(self, fromAddr, toAddr, subject, body, attachment):
		super(Email, self).__init__()
		self.fromAddr = fromAddr
		self.toAddr = toAddr
		self.subject = subject
		self.body = body
		self.hasAttachment = False

		if attachment != None and attachment != "":
			self.hasAttachment = True
			self.attachment = attachment
			self.attachmentName = attachment.get("attachmentName")
			#self.attachmentPath = attachment["attachmentPath"]
		
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
		

		if self.hasAttachment == True:
			filename = self.attachmentName
			#attachment = open(self.attachmentPath, "rb")
			print("The attached filename is:" + filename)
			print("The bucket name is:" + BUCKET_NAME)

			s3 = boto3.resource(
		        's3',
		        aws_access_key_id=os.environ['S3_KEY'],
		        aws_secret_access_key=os.environ['S3_SECRET'],
		        config=Config(signature_version='s3v4')
		        )
			attachment = s3.Object(BUCKET_NAME, filename)

			part = MIMEBase('application', 'octet-stream')
			#part.set_payload((attachment).read())
			part.set_payload((attachment).get()['Body'].read())
			encoders.encode_base64(part)
			part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
			 
			msg.attach(part)

		server = smtplib.SMTP('smtp.gmail.com', 587)
		server.ehlo()
		server.starttls()
		server.ehlo()
		server.login(self.fromAddr, os.environ['GMAIL_SECRET'])
		text = msg.as_string()
		server.sendmail(self.fromAddr, self.toAddr, text)
		server.quit()


	def sendSparkPostEmail(self):
		print("Should send a email via spark")


	def getFromAddress(self):
		return self.fromAddr

	def setFromAddress(self, fromAddr):
		self.fromAddr = fromAddr


	def getToAddress(self):
		return self.toAddr

	def setToAddress(self, toAddr):
		self.toAddr = toAddr


	def getSubject(self):
		return self.subject

	def setSubject(self, subject):
		self.subject = subject

	def getBody(self):
		return self.body

	def setBody(self, body):
		self.body = body

	def getAttachment(self):
		return self.attachment

	def setAttachment(self, attachment):
		if attachment != None and attachment != "":
			self.hasAttachment = True
			self.attachment = attachment
			self.attachmentName = attachment.get("attachmentName")
