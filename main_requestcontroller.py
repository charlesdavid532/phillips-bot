from welcome import WelcomeResponse
from sales_requestcontroller import SalesRequestController
from constants import Constants
from chart_controller import ChartController
from email_request_controller import EmailRequestController
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
	        parsedData = self.parseFreeDeliveryRequest(self.requestData)        
	        self.responseData = self.makePermissionsResult(parsedData["speech"], [], ["NAME", "DEVICE_PRECISE_LOCATION"])        
	    elif self.requestData.get("result").get("action") == "compare.location":
	        parsedData = self.compareDeliveryLocation(self.requestData)
	        self.responseData = self.makeContextWebhookResult(parsedData["speech"], [])  
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


	def makePermissionsResult(speech, context, permissionList):

	    dataJSON = {}
	    dataJSON["google"] = {}
	    googleJSON = dataJSON["google"]

	    googleJSON["expectUserResponse"] = True
	    googleJSON["systemIntent"] = {}

	    #possibleIntents = []

	    permissionDict = googleJSON["systemIntent"]
	    permissionDict["intent"] = "actions.intent.PERMISSION"
	    permissionDict["data"] = {}

	    inputValueDataDict = permissionDict["data"]
	    inputValueDataDict["@type"] = "type.googleapis.com/google.actions.v2.PermissionValueSpec"
	    inputValueDataDict["optContext"] = "To deliver your order"
	    inputValueDataDict["permissions"] = permissionList

	    #possibleIntents.append(permissionDict)

	    return {
	        "speech": speech,
	        "displayText": speech,
	        "data": dataJSON,
	        "contextOut": context,
	        "source": "phillips-bot"
	    }

	def makePermissionsResultV1(speech, context, permissionList):
	    possibleIntents = []

	    permissionDict = {}
	    permissionDict["intent"] = "assistant.intent.actions.PERMISSION"
	    permissionDict["input_value_spec"] = {}

	    inputValueSpecDict = permissionDict["input_value_spec"]
	    inputValueSpecDict["permission_value_spec"] = {}

	    permission_value_spec = inputValueSpecDict["permission_value_spec"]

	    permission_value_spec["optContext"] = "To deliver your order"
	    permission_value_spec["permissions"] = permissionList

	    possibleIntents.append(permissionDict)

	    return {
	        "speech": speech,
	        "displayText": speech,
	        "possibleIntents": possibleIntents,
	        "contextOut": context,
	        "source": "phillips-bot"
	    }

	    
	def parseFreeDeliveryRequest(req):
	    
	    return {
	        "speech" : "I need access to your device location to perform this task"
	    }

	def compareDeliveryLocation(req):
	    #Check to see if the permission has already been given
	    if req.get('originalRequest').get('data').get('device') != None:
	        devcoords = req.get('originalRequest').get('data').get('device').get('location').get('coordinates')
	        print("The latitude is::" + str(devcoords.get('latitude')))
	        print("The longitude is::" + str(devcoords.get('longitude')))
	        return {
	            "speech" : "Yes you are at::" + str(devcoords.get('latitude')) + " latitude and " + str(devcoords.get('longitude')) + " longitude"
	        }

	    return {
	        "speech" : "Could not get your location"
	    }