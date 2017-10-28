import os
import boto3
from botocore.client import Config

class AmazonS3(object):
	"""Deals with all things related to storing/retreiving stuff from Amazon S3"""
	def __init__(self, bucketname):
		super(AmazonS3, self).__init__()

		self.s3 = boto3.resource('s3',aws_access_key_id=os.environ['S3_KEY'],aws_secret_access_key=os.environ['S3_SECRET'],config=Config(signature_version='s3v4'))
		self.bucketname = bucketname

	def saveResourceToAWS(self, img_data, img_name, content_type, bucketname):
		print("saving resource to aws in amazon s3")
		#self.s3.Bucket(BUCKET_NAME).put_object(Key=img_name, Body=img_data, ContentType=content_type)
		self.s3.Bucket(bucketname).put_object(Key=img_name, Body=img_data, ContentType=content_type)
		print("Saved resource to aws")
		

	def getS3Object(self, bucketname, filename):
		return self.s3.Object(bucketname, filename)


	def readS3Object(self, bucketname, filename):
		attachment = self.getS3Object(bucketname, filename)
		return (attachment).get()['Body'].read()


	