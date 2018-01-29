
from welcome import WelcomeResponse
from sales_requestcontroller import SalesRequestController
from constants import Constants
from chart_controller import ChartController
from email_request_controller import EmailRequestController
from free_delivery_controller import FreeDeliveryController
from selected_list_item import SelectedListItem
from carousel import Carousel
from custom_list import List
from suggestion_chip import SuggestionChip
import urllib
from fb_share_dialog_controller import FBShareDialogController
from daily_update_permission_controller import DailyUpdatePermissionController
class MainRequestController(object):
	"""Handles the request from api.ai"""
	def __init__(self, data, mongo, userDataObj):
		super(MainRequestController, self).__init__()
		self.requestData = data
		self.responseData = None
		self.mongo = mongo
		self.userDataObj = userDataObj
		self.setSourceAsGoogle()



	def processRequest(self):
		print('hi')
		if self.requestData.get("result").get("action") == "sales.statistics":	    	
			salesRequestController = SalesRequestController(self.requestData, self.mongo)
			salesResponseData = salesRequestController.getSalesResponse()
			self.responseData = self.makeContextWebhookResult(salesResponseData["speech"], salesResponseData["context-list"])
		elif self.requestData.get("result").get("action") == "detailed.statistics":			
			salesRequestController = SalesRequestController(self.requestData, self.mongo)
			salesRequestController.setIsContext(Constants.getStrDetailedSalesContext())
			salesResponseData = salesRequestController.getSalesResponse()
			self.responseData = self.makeContextWebhookResult(salesResponseData["speech"], salesResponseData["context-list"])
		elif self.requestData.get("result").get("action") == "free.delivery":
			freeDelControllerObj = FreeDeliveryController(self.requestData, self.mongo)
			freeDelControllerObj.setSource(self.source)
			self.responseData = freeDelControllerObj.getPermissionJSON()
			'''
			parsedData = self.parseFreeDeliveryRequest(self.requestData)        
			self.responseData = self.makePermissionsResult(parsedData["speech"], [], ["NAME", "DEVICE_PRECISE_LOCATION"])        
			'''
		elif self.requestData.get("result").get("action") == "compare.location":
			freeDelControllerObj = FreeDeliveryController(self.requestData, self.mongo)
			freeDelControllerObj.setSource(self.source)
			freeDelControllerObj.setIsPermissionGiven(True)
			compareLocationData = freeDelControllerObj.compareDeliveryLocation()
			self.responseData = self.makeContextWebhookResult(compareLocationData["speech"], []) 
		elif self.requestData.get("result").get("action") == "show.fb.dialog":
			fbShareDialogControllerObj = FBShareDialogController()
			self.responseData = fbShareDialogControllerObj.getJSONResponse()
		elif self.requestData.get("result").get("action") == "daily.offer.permission":
			dailyUpdatePermissionControllerObj = DailyUpdatePermissionController()
			dailyUpdatePermissionControllerObj.setIntentName("show-daily-offer")
			self.responseData = dailyUpdatePermissionControllerObj.getRequestPermissionJSON()
		elif self.requestData.get("result").get("action") == "finish.update.setup":
			dailyUpdatePermissionControllerObj = DailyUpdatePermissionController()
			dailyUpdatePermissionControllerObj.setResultText("Ok we will send you daily offers")
			permissionResponseData = dailyUpdatePermissionControllerObj.getResultPermissionJSON()
			self.responseData = self.makeContextWebhookResult(permissionResponseData, []) 
		elif self.requestData.get("result").get("action") == "product.chart":
			chartController = ChartController(self.requestData, self.mongo)
			self.responseData = chartController.getChartResponse()
			#self.responseData = generateProductChartController(self.requestData.get("result").get('parameters'))
		elif self.requestData.get("result").get("action") == "detailed.chart":
			chartController = ChartController(self.requestData, self.mongo)
			chartController.setIsContext(Constants.getStrDetailedChartContext())
			self.responseData = chartController.getChartResponse()
			#self.responseData = parseContextGenerateProductChartController(self.requestData.get("result"))
		elif self.requestData.get("result").get("action") == "convert.chart":
			chartController = ChartController(self.requestData, self.mongo)
			chartController.setSource(self.source)
			chartController.setIsContext(Constants.getStrDrawChartContext())
			self.responseData = chartController.getChartResponse()
			#self.responseData = convertTextToProductChartController(self.requestData.get("result"))
		elif self.requestData.get("result").get("action") == "send.customEmail":
			emailControllerObj = EmailRequestController(self.requestData,self.mongo)
			emailControllerObj.setIsContext(Constants.getStrChartEmailContext())
			self.responseData = emailControllerObj.getEmailResponse()
			#self.responseData = generateEmailController(self.requestData.get("result"))
		elif self.requestData.get("result").get("action") == "welcome.intent":
			welcomeResponseObj = WelcomeResponse(self.requestData)
			welcomeResponseObj.setSource(self.source)
			self.responseData = welcomeResponseObj.getWelcomeResponse()
		elif self.requestData.get("result").get("action") == "showAllUsers":
			self.responseData = makeListOfAllUsers(self.requestData)
		elif self.requestData.get("result").get("action") == "detailed.bio":
			self.responseData = showDetailedBio(self.requestData)
		elif self.requestData.get("result").get("action") == "application.close":
			self.responseData = closeApplication(self.requestData)    
		elif self.requestData.get("result").get("action") == "detailed.list":
			'''
			firstInput = self.requestData["originalRequest"]["data"]["inputs"][0]
			if 'arguments' in firstInput:
				optionVal = firstInput["arguments"][0]["textValue"]
				print("The option chosen:::")
				print(optionVal)
			'''
			#selectedListItemObj = SelectedListItem(self.requestData)
			SelectedListItem.set_provider_none()
			selectedListItemObj = SelectedListItem.get_provider(self.source, self.requestData)
			optionVal = selectedListItemObj.getSelectedListItem()
			if optionVal == False:
				optionVal = "Could not find option chosen"
			self.responseData = self.makeContextWebhookResult("The option chosen:::"+optionVal, [])
		elif self.requestData.get("result").get("action") == "show.list":
			'''
			simpleResponse = []
			simpleResponse.append("This is your desired carousel")
			#myCarousel = Carousel(simpleResponse)
			Carousel.set_provider_none()
			myCarousel = Carousel.get_provider(self.source, simpleResponse)
			myCarousel.addCarouselItem("1", "First", "abc", "The first item in the list", "https://s3.ap-south-1.amazonaws.com/tonibot-bucket/cdavid.jpg", "Default acc text")
			myCarousel.addCarouselItem("2", "Second", "def", "The second item in the list", "https://s3.ap-south-1.amazonaws.com/tonibot-bucket/charlesdavid531.jpg", "Default acc text")

			self.responseData = myCarousel.getCarouselResponse()
			'''
			simpleResponse = []
			simpleResponse.append("This is your desired list")
			List.set_provider_none()
			myList = List.get_provider(self.source, simpleResponse)
			myList.addListItem("1", "First", "abc", "The first item in the list", "https://s3.ap-south-1.amazonaws.com/tonibot-bucket/cdavid.jpg", "Default acc text")
			myList.addListItem("2", "Second", "def", "The second item in the list", "https://s3.ap-south-1.amazonaws.com/tonibot-bucket/charlesdavid531.jpg", "Default acc text")

			self.responseData = myList.getListResponse()

		elif self.requestData.get("result").get("action") == "show.chip":			
			simpleResponse = []
			simpleResponse.append("This is your desired suggestion chip")
			sugList = []
			sugList.append("Show digital employees")
			sugList.append("Bye doctor dashboard")
			sugList.append("Receive daily offers")

			SuggestionChip.set_provider_none()
			mySuggestionChip = SuggestionChip.get_provider(self.source, simpleResponse)
			mySuggestionChip.addSugTitles(sugList)

			paramVars = {}
			paramVars['selectedCouponCode'] = "abcd"
			FBShareDialogURI = "https://phillipsbot.herokuapp.com/facebook/share" + '?' + urllib.parse.urlencode(paramVars)
			'''
			mySuggestionChipResponse.addLinkOutSuggestion("Share on Facebook", "https://flobots.herokuapp.com/facebook/share")
			'''
			mySuggestionChip.addLinkOutSuggestion("Share on Facebook", FBShareDialogURI)			
			#This is meant only for facebook
			if self.isSourceFacebook() == True:
				if self.userDataObj.hasFBUserLoggedIn(self.requestData.get("originalRequest").get("data").get("sender").get("id")) != True:
					mySuggestionChip.addLoginBtn("https://phillipsbot.herokuapp.com/authorize/facebook")

			self.responseData = mySuggestionChip.getSuggestionChipResponse()
   
		elif self.requestData.get("result").get("action") == "time.timeperiod":	        
			return {}
		else:
			return {}
		return self.responseData

	def setRequestData(self, data):
		self.requestData = data

	def getRequestData(self):
		return self.requestData

	def getResponseData(self):
		return self.responseData

	def setSourceAsFacebook(self):
		self.source = 'facebook'

	def setSourceAsGoogle(self):
		self.source = 'google'

	def getSource(self):
		return self.source

	def isSourceFacebook(self):
		if self.source == 'facebook':
			return True
		else:
			return False
	'''
	This is a very temp function. It is used to just create a sample response in JSON format
	'''
	def makeContextWebhookResult(self, speech, context):

		if self.isSourceFacebook():
			return self.FBmakeContextWebhookResult(speech, context)

		return {
		    "speech": speech,
		    "displayText": speech,
		    # "data": data,
		    "contextOut": context,
		    "source": "phillips-bot"
		}


	def FBmakeContextWebhookResult(self, speech, context):

		return {
			"speech": speech,
		    "displayText": speech,
		    "data": {
		    	"facebook": {
		    		"text": speech
		    	}
		    },
		    "contextOut": context,
		    "source": "phillips-bot"
		}




	    
	

	