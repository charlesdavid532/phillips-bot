import uuid
from constants import Constants
from amazon_s3 import AmazonS3
from product_chart_controller import ProductChartController
from context_request import ContextRequest
from context_response import ContextResponse
from context_responseList import ContextResponseList
from card import Card
from parser import Parser
class ChartController(object):
	"""docstring for ChartController"""
	def __init__(self, requestData, mongo):
		super(ChartController, self).__init__()
		self.requestData = requestData
		self.userParameters = self.requestData.get("result").get('parameters')
		self.removeIsContext()
		self.cities = None
		self.product = None
		self.period = None
		self.chartType = None
		self.mainChartFeature = None
		self.mongo = mongo
		
	def setIsContext(self, contextName):
		self.isContext = True
		userContext = self.requestData.get("result").get('contexts')
		#Creating a context request class
		myContextRequest = ContextRequest(userContext)

		# This context is an array. Parse this array until you get the required context
		#detailedSalesContext = myContextRequest.getAppropriateUserContext("detailed_sales")
		detailedChartContext = myContextRequest.getAppropriateUserContext(contextName)

		# If the context is not set		
		if myContextRequest.getIsContextSet() == False:
			return detailedChartContext

		self.contextParameters = detailedChartContext.get('parameters')

	def removeIsContext(self):
		self.isContext = False
		self.contextParameters = None

	def getIsContext(self):
		return self.isContext


	def getChartResponse(self):
		if self.getIsContext() == False:
			self.cities, self.products, self.period, self.chartType, self.mainChartFeature = self.parseParameters()
		else:
			self.cities, self.products, self.period, self.chartType, self.mainChartFeature = self.parseContextParameters()


		img_data = self.drawMainChartFeatureChart(self.cities, self.products, self.period, self.chartType, self.mainChartFeature)

		self.storeImageInAWS(img_data)

		contextResponseMainList = self.createChartContext()

		simpleResponse = []
		simpleResponse.append("Here is the product wise chart requested")
		sugList = []
		sugList.append("Show digital employees")
		sugList.append("Bye doctor dashboard")

		title = "Dr. Dashboard"
		formattedText = "Phillips bot a.k.a. Dr. Dashboard is designed for voice enabled financial reporting"
		imgURL = self.awsImageFileName
		imgAccText = "Default accessibility text"

		myCard = Card(simpleResponse, formattedText, imgURL, imgAccText)
		myCard.addTitle(title)
		myCard.addSugTitles(sugList)
		myCard.addOutputContext(contextResponseMainList.getContextJSONResponse())
		myCard.addExpectedUserResponse()

		return myCard.getCardResponse()



	'''
	This function parses the main chart feature and draws the appropriate chart
	'''
	def drawMainChartFeatureChart(self):

		mChartFeature = self.mainChartFeature["main-chart-feature"]

		if mChartFeature == Constants.getStrProduct():
			prodChartContrObj = ProductChartController(self.cities, self.products, self.period, self.chartType, self.mainChartFeature, self.mongo)
			return prodChartContrObj.drawChart()	        
		elif mChartFeature == Constants.getStrCity():
			print("This should return city wise revenues")
		elif mChartFeature == Constants.getStrState():
			print("This should return state wise revenues")
		elif mChartFeature == Constants.getStrRegion():
			print("This should return region wise revenues")
		else:
			print("Default returns product wise revenues")
			prodChartContrObj = ProductChartController(self.cities, self.products, self.period, self.chartType, self.mainChartFeature, self.mongo)
			return prodChartContrObj.drawChart()		        



	def parseParameters(self):
		myParser = Parser(self.mongo)
		myParser.setUserParameters(self.userParameters)

		cities = myParser.parseUserRegion(self.userParameters)
		products = myParser.parseUserProducts(self.userParameters)
		period = myParser.parseUserPeriod(self.userParameters.get('period'))
		chartType = myParser.parseUserChartType(self.userParameters)
		mainChartFeature = myParser.parseUserMainChartFeature(self.userParameters)

		return cities, products, period, chartType, mainChartFeature


	def parseContextParameters(self):
		myParser = Parser(self.mongo)
		myParser.setUserParameters(self.userParameters)
		myParser.setContextUserParameters(self.contextParameters)

		cities = myParser.parseContextUserRegion(self.userParameters, self.contextParameters)
		products = myParser.parseContextUserProducts(self.userParameters, self.contextParameters)
		period = myParser.parseContextUserPeriod(self.userParameters.get('period'), self.contextParameters.get('context-period'))
		chartType = myParser.parseContextUserChartType(self.userParameters, self.contextParameters)
		mainChartFeature = myParser.parseContextUserMainChartFeature(self.userParameters, self.contextParameters)

		return cities, products, period, chartType, mainChartFeature


	def storeImageInAWS(self, img_data):
		self.imageFileName = uuid.uuid4().hex[:6].upper()
		#imageFileName = 'product'
		self.imageFileName += '.png'
		print ("The image file name is:"+ self.imageFileName)
		self.awsImageFileName = Constants.getAWSBucketURL() + self.imageFileName


		myAmazonS3 = AmazonS3(Constants.getAWSBucketName())
		myAmazonS3.saveResourceToAWS(img_data, self.imageFileName, Constants.getStrImageContentType(), Constants.getAWSBucketName())


	def createChartContext(self):

		#Creating the email context object
		emailContextResponseObject = ContextResponse(Constants.getStrChartEmailContext(), 5)
		emailContextResponseObject.addFeature("context-attachment-name", self.imageFileName)
		#Creating the chart context object
		detailedChartContextResponseObject = ContextResponse(Constants.getStrDetailedChartContext(), 1)
		detailedChartContextResponseObject.addFeature("context-geo-city-us", self.cities["context-geo-city-us"])
		detailedChartContextResponseObject.addFeature("context-geo-state-us", self.cities["context-geo-state-us"])
		detailedChartContextResponseObject.addFeature("context-region", self.cities["context-region"])
		detailedChartContextResponseObject.addFeature("context-product", self.products["context-product"])
		detailedChartContextResponseObject.addFeature("context-period", self.period["context-period"])
		detailedChartContextResponseObject.addFeature("context-chart-type", self.chartType["context-chart-type"])
		detailedChartContextResponseObject.addFeature("context-main-chart-feature", self.mainChartFeature["context-main-chart-feature"])

		contextResponseMainList = ContextResponseList()
		contextResponseMainList.addContext(emailContextResponseObject)
		contextResponseMainList.addContext(detailedChartContextResponseObject)

		return contextResponseMainList
