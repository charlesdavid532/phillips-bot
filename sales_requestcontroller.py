from context_request import ContextRequest
from context_response import ContextResponse
from context_responseList import ContextResponseList
from parser import Parser
from sales_responsecontroller import SalesResponseController
from datetime import datetime as dt
class SalesRequestController(object):
	"""Handles the sales request"""
	def __init__(self, requestData, mongo):
		super(SalesRequestController, self).__init__()
		self.requestData = requestData
		self.userParameters = self.requestData.get("result").get('parameters')
		self.removeIsContext()
		self.mongo = mongo
		self.cities = None
		self.product = None
		self.period = None
		self.salesRev = None

	#TODO:: Context handling can be done in the main controller
	def setIsContext(self, contextName):
		self.isContext = True
		userContext = self.requestData.get("result").get('contexts')
		#Creating a context request class
		myContextRequest = ContextRequest(userContext)

		# This context is an array. Parse this array until you get the required context
		#detailedSalesContext = myContextRequest.getAppropriateUserContext("detailed_sales")
		detailedSalesContext = myContextRequest.getAppropriateUserContext(contextName)

		# If the context is not set		
		if myContextRequest.getIsContextSet() == False:
			return detailedSalesContext

		self.contextParameters = detailedSalesContext.get('parameters')

	def removeIsContext(self):
		self.isContext = False
		self.contextParameters = None

	def getIsContext(self):
		return self.isContext


	def getSalesResponse(self):
		if self.getIsContext() == False:
			self.cities, self.product, self.period = self.parseParameters()
		else:
			self.cities, self.product, self.period = self.parseContextParameters()

		self.salesRev = self.getSalesAmount(self.period, self.cities["cities"], self.product["product"])

		contextResponseMainList = self.createSalesContext()

		if self.getIsContext() == False:
			speech = self.getSpeechResponseForSales()
		else:
			speech = self.getContextSpeechResponseForSales()

		return {
		    "speech": speech,
		    "context-list": contextResponseMainList.getContextJSONResponse()
		    }



	def parseParameters(self):
		myParser = Parser(self.mongo)
		myParser.setUserParameters(self.userParameters)

		cities = myParser.parseUserRegion(self.userParameters)
		product = myParser.parseUserProduct(self.userParameters)
		period = myParser.parseUserPeriod(self.userParameters.get('period'))

		return cities, product, period


	def parseContextParameters(self):
		myParser = Parser(self.mongo)
		myParser.setUserParameters(self.userParameters)
		myParser.setContextUserParameters(self.contextParameters)

		cities = myParser.parseContextUserRegion(self.userParameters, self.contextParameters)
		product = myParser.parseContextUserProduct(self.userParameters, self.contextParameters)
		period = myParser.parseContextUserPeriod(self.userParameters.get('period'), self.contextParameters.get('context-period'))

		return cities, product, period
		

	'''
	This function returns the sales for the specified productId, cities, period
	TODO: Change query into an aggregation function of mongo db in order to expedite the process & lift load from python
	'''
	def getSalesAmount(self, period, cities, productId):
		print ("In get sales amount")
		print ("The start date is:" + str(period["startDate"]))
		print ("The end date is:" + str(period["endDate"]))
		print ("the first city is:" + cities[0])
		print ("The product id is:" + productId)

		salesRev = 0
		salesData = self.mongo.db.sales1
		startDate = period["startDate"]
		endDate = period["endDate"]
		'''
		If it is a single date else it is a range
		'''
		if endDate == "":
		    try: 
		        for s in salesData.find({'pId': productId, 'city': {'$in':cities},'date': startDate}):
		            print("The sales revenue is:"+s['salesRev'])
		            salesRev = salesRev + int(s['salesRev'])
		        
		        print("The cumulative sales revenue for date is:" + str(salesRev))
		        #return "The cumulative sales revenue is:" + str(salesRev)
		        return salesRev
		        
		    except Exception:
		        print("Could not query database")
		        return ''
		else:
		    try: 
		        for s in salesData.find({'pId': productId, 'city': {'$in':cities}}):
		            print ("The date is:" + s['date'])
		            if (dt.strptime(s['date'], "%Y-%m-%d") >= dt.strptime(startDate, "%Y-%m-%d")) and (dt.strptime(s['date'], "%Y-%m-%d") <= dt.strptime(endDate, "%Y-%m-%d")):
		                print ("Inside if")
		                print("The sales revenue is:"+s['salesRev'])
		                salesRev = salesRev + int(s['salesRev'])
		        
		        print("The cumulative sales revenue for date range is:" + str(salesRev))
		        #return "The cumulative sales revenue is:" + str(salesRev)
		        return salesRev

		    except Exception:
		        print("Could not query database")
		        return ''


	def createSalesContext(self):
		# Creating the detailed sales context object
		detailedSalesContextResponseObject = ContextResponse(Constants.getStrDetailedSalesContext(), 1)
		detailedSalesContextResponseObject.addFeature("context-geo-city-us", self.cities["context-geo-city-us"])
		detailedSalesContextResponseObject.addFeature("context-geo-state-us", self.cities["context-geo-state-us"])
		detailedSalesContextResponseObject.addFeature("context-region", self.cities["context-region"])
		detailedSalesContextResponseObject.addFeature("context-product", self.product["context-product"])
		detailedSalesContextResponseObject.addFeature("context-period", self.period["context-period"])

		#Creating the chart context object
		drawChartContextResponseObject = ContextResponse(Constants.getStrDrawChartContext(), 1)
		drawChartContextResponseObject.addFeature("context-geo-city-us", self.cities["context-geo-city-us"])
		drawChartContextResponseObject.addFeature("context-geo-state-us", self.cities["context-geo-state-us"])
		drawChartContextResponseObject.addFeature("context-region", self.cities["context-region"])
		drawChartContextResponseObject.addFeature("context-product", self.product["context-product"])
		drawChartContextResponseObject.addFeature("context-period", self.period["context-period"])
		drawChartContextResponseObject.addFeature("context-chart-type", "")
		drawChartContextResponseObject.addFeature("context-main-chart-feature", "")

		contextResponseMainList = ContextResponseList()
		contextResponseMainList.addContext(detailedSalesContextResponseObject)
		contextResponseMainList.addContext(drawChartContextResponseObject)

		return contextResponseMainList


	def getSpeechResponseForSales(self):
		myResponse = SalesResponseController(self.userParameters, self.salesRev, self.period)
		return myResponse.getSalesResponseStr()


	def getContextSpeechResponseForSales(self):
		myResponse = SalesResponseController(self.userParameters, self.salesRev, self.period)
		myResponse.setIsContext(self.contextParameters)
		return myResponse.getSalesResponseStr()
		