from card import Card
from constants import Constants
class WelcomeResponse(object):
	"""Handles the welcome request"""
	def __init__(self, requestData):
		super(WelcomeResponse, self).__init__()
		self.requestData = requestData
		self.source = None


	def getWelcomeResponse(self):
		print ("Inside show welcome intent")
		

		simpleResponse = []
		simpleResponse.append("Hi, I am Dr. Dashboard - a sales tracker. The suggestions below are some of the things I can do! At any time if you want to leave the application say Bye Dr. Dashboard! What can I do for you?")
		sugList = []
		sugList.append("Show digital employees")
		sugList.append("Bye doctor dashboard")
		sugList.append("Receive daily offers")
		title = "Dr. Dashboard"
		formattedText = "Phillips bot a.k.a. Dr. Dashboard is designed for voice enabled financial reporting"
		imgURL = Constants.getBlueBotURL()
		imgAccText = "Default accessibility text"


		#myCard = Card(simpleResponse, formattedText, imgURL, imgAccText)
		Card.set_provider_none()
		myCard = Card.get_provider(self.source, simpleResponse, formattedText, imgURL, imgAccText)
		myCard.addTitle(title)
		myCard.addSugTitles(sugList)
		myCard.addExpectedUserResponse()
		

		return myCard.getCardResponse()
		
	def setSource(self, source):
		self.source = source