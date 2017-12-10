from datetime import datetime as dt
from datetime import timedelta
class DateUtils(object):
	"""docstring for DateUtils"""
	def __init__(self):
		super(DateUtils, self).__init__()


	@staticmethod
	def getCurrentDateAndTime():
		return dt.now()

	@staticmethod
	def getStrCurrentDateAndTime():
		return DateUtils.getCurrentDateAndTime().strftime("%Y-%m-%d %H:%M:%S")

	@staticmethod
	def getFutureDateAndTimeMins(mins):
		return DateUtils.getCurrentDateAndTime() + timedelta(minutes=mins)

	@staticmethod
	def getStrFutureDateAndTime(mins):	    
	    return DateUtils.getFutureDateAndTimeMins(mins).strftime("%Y-%m-%d %H:%M:%S")

	@staticmethod
	def getFutureDateAndTimeSecs(secs):
		return DateUtils.getCurrentDateAndTime() + timedelta(seconds=secs)

	@staticmethod
	def getStrFutureDateAndTimeSecs(secs):
		return DateUtils.getFutureDateAndTimeSecs(secs).strftime("%Y-%m-%d %H:%M:%S")


	'''
	Compares date time 1 with date time 2
	Returns True if 1 < 2
	Else False
	'''
	@staticmethod
	def compareDateAndTime(dateTime1, dateTime2):
		if dt.strptime(dateTime1, "%Y-%m-%d %H:%M:%S")  < dt.strptime(dateTime2, "%Y-%m-%d %H:%M:%S"):
			return True
		else:
			return False
		