from welcome import WelcomeResponse
from sales_requestcontroller import SalesRequestController
from constants import Constants
from chart_controller import ChartController
from email_request_controller import EmailRequestController
from free_delivery_controller import FreeDeliveryController
class MainRequestController(object):
	"""Handles the request from api.ai"""
	def __init__(self, data, mongo):
		super(MainRequestController, self).__init__()
		self.requestData = data
		self.responseData = None
		self.mongo = mongo



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
			self.responseData = freeDelControllerObj.getPermissionJSON()
			'''
			parsedData = self.parseFreeDeliveryRequest(self.requestData)        
			self.responseData = self.makePermissionsResult(parsedData["speech"], [], ["NAME", "DEVICE_PRECISE_LOCATION"])        
			'''
		elif self.requestData.get("result").get("action") == "compare.location":
			freeDelControllerObj = FreeDeliveryController(self.requestData, self.mongo)
			freeDelControllerObj.setIsPermissionGiven(True)
			compareLocationData = freeDelControllerObj.compareDeliveryLocation()
			self.responseData = self.makeContextWebhookResult(compareLocationData["speech"], [])  
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
			self.responseData = welcomeResponseObj.getWelcomeResponse()
		elif self.requestData.get("result").get("action") == "showAllUsers":
			self.responseData = makeListOfAllUsers(self.requestData)
		elif self.requestData.get("result").get("action") == "detailed.bio":
			self.responseData = showDetailedBio(self.requestData)
		elif self.requestData.get("result").get("action") == "application.close":
			self.responseData = closeApplication(self.requestData)    
		elif self.requestData.get("result").get("action") == "detailed.list":
			firstInput = self.requestData["originalRequest"]["data"]["inputs"][0]
		    if 'arguments' in firstInput:
		        optionVal = firstInput["arguments"][0]["textValue"]
		        print("The option chosen:::")
		        print(optionVal)
			self.responseData = self.makeContextWebhookResult("The option chosen:::"+optionVal, [])    
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



	'''
	This is a very temp function. It is used to just create a sample response in JSON format
	'''
	def makeContextWebhookResult(self, speech, context):

		return {
		    "speech": speech,
		    "displayText": speech,
		    # "data": data,
		    "contextOut": context,
		    "source": "phillips-bot"
		}




	    
	

	