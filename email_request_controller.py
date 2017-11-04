from parser import Parser
from custom_email import Email
from card import Card
class EmailRequestController(object):
	"""docstring for EmailRequestController"""
	def __init__(self, requestData, mongo):
		super(EmailRequestController, self).__init__()
		self.requestData = requestData
		self.userParameters = self.requestData.get("result").get('parameters')
		self.removeIsContext()
		self.mongo = mongo


	def setIsContext(self, contextName):
		self.isContext = True
		userContext = self.requestData.get("result").get('contexts')
		#Creating a context request class
		myContextRequest = ContextRequest(userContext)

		# This context is an array. Parse this array until you get the required context
		#detailedSalesContext = myContextRequest.getAppropriateUserContext("detailed_sales")
		emailContext = myContextRequest.getAppropriateUserContext(contextName)

		# If the context is not set		
		if myContextRequest.getIsContextSet() == False:
			return emailContext

		self.contextParameters = emailContext.get('parameters')

	def removeIsContext(self):
		self.isContext = False
		self.contextParameters = None

	def getIsContext(self):
		return self.isContext


	def getEmailResponse(self):
		myParser = Parser(self.mongo)
		myParser.setUserParameters(self.userParameters)
		emailParameters = myParser.parseContextEmail(self.userParameters, self.contextParameters)

		print ("After email Parameters")
		print ("the attachment name is:"+ emailParameters['attachment-name'])
		print ("Email to be sent to:"+ emailParameters['email-to'])
		'''
		Sending an email trial
		'''
		myAttachment = {}
		myAttachment["attachmentName"] = emailParameters['attachment-name']
		#myAttachment["attachmentPath"] = "https://s3.ap-south-1.amazonaws.com/tonibot-bucket/1A0119.png"
		myEmail = Email("charlesdavid2711@gmail.com", emailParameters['email-to'], "Product wise sales report","As requested please find attached the product wise sales report",myAttachment)
		myEmail.sendEmail()


		simpleResponse = []
		simpleResponse.append("Email sent successfully! What else can I do for you?")

		sugList = []
		sugList.append("Show digital employees")
		sugList.append("Bye doctor dashboard")

		title = "Dr. Dashboard"
		formattedText = "Phillips bot a.k.a. Dr. Dashboard is designed for voice enabled financial reporting"


		imgURL = Constants.getBlueBotURL()
		imgAccText = "Default accessibility text"

		myCard = Card(simpleResponse, formattedText, imgURL, imgAccText)
		myCard.addTitle(title)
		myCard.addSugTitles(sugList)
		myCard.addExpectedUserResponse()

		return myCard.getCardResponse()
		