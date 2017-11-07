from datetime import datetime as dt
from constants import Constants
from chart import Chart
from bar_chart import BarChart
from pie_chart import PieChart
class ProductChartController(object):
	"""docstring for ProductChartController"""
	def __init__(self, cities, products, period, chartType, mainChartFeature, mongo):
		super(ProductChartController, self).__init__()
		self.cities = cities
		self.products = products
		self.period = period
		self.chartType = chartType
		self.mainChartFeature = mainChartFeature
		self.mongo = mongo

	def drawChart(self):
		productRevenues = self.getProductWiseRevenue(self.period, self.cities["cities"], self.products["product"])

		if productRevenues == []:
			print ("There is a problem no product revenues were generated")
			return ""
		# Call a function that generates the chart
		return self.drawProductChart(productRevenues, self.chartType["chart-type"], Constants.getStrProducts(), Constants.getStrRevenues(),
									 Constants.getStrProductWiseRevenues())
	'''
	This function returns product wise revenues (List of objects : product, salesRevenue) for the specified productId, cities, period
	TODO: Change query into an aggregation function of mongo db in order to expedite the process & lift load from python
	'''
	def getProductWiseRevenue(self, period, cities, productIds):
		print ("In get product wise revenue")
		print ("The start date is:" + str(period["startDate"]))
		print ("The end date is:" + str(period["endDate"]))
		print ("the first city is:" + cities[0])
		print ("The first product id is:" + productIds[0])


		productRevenues = []
		salesRev = 0
		salesData = self.mongo.db.sales1
		startDate = period["startDate"]
		endDate = period["endDate"]
		'''
		If it is a single date else it is a range
		'''
		if endDate == "":
			for id in range(0, len(productIds)):
				prodRev = {}
				salesRev = 0

				try: 
					for s in salesData.find({'pId': productIds[id], 'city': {'$in':cities},'date': startDate}):
						print("The sales revenue is:"+s['salesRev'])
						salesRev = salesRev + int(s['salesRev'])

					print("The cumulative sales revenue for this product is:" + str(salesRev))

					prodRev['product'] = self.getPNameFromPId(productIds[id])
					prodRev['salesRevenue'] = salesRev
					productRevenues.append(prodRev)

				except Exception:
					print("Could not query database")
					return []

			return productRevenues
		else:
			for id in range(0, len(productIds)):
				prodRev = {}
				salesRev = 0

				try:
					for s in salesData.find({'pId': productIds[id], 'city': {'$in':cities}}):
						print ("The date is:" + s['date'])
						if (dt.strptime(s['date'], "%Y-%m-%d") >= dt.strptime(startDate, "%Y-%m-%d")) and (dt.strptime(s['date'], "%Y-%m-%d") <= dt.strptime(endDate, "%Y-%m-%d")):
							print ("Inside if")
							print("The sales revenue is:"+s['salesRev'])
							salesRev = salesRev + int(s['salesRev'])

					print("The cumulative sales revenue for date range for this product is:" + str(salesRev))

					prodRev['product'] = self.getPNameFromPId(productIds[id])
					prodRev['salesRevenue'] = salesRev
					productRevenues.append(prodRev)

				except Exception:
				    print("Could not query database")
				    return []


		return productRevenues
		

	def getPNameFromPId(self, pId):
		print ("This function should return a product name from a product id")


		prodData = self.mongo.db.products
		try:
			prodCur = prodData.find({            
			    "pId":pId
			    }, {
			    "pName": 1
			    })

			for p in prodCur:
				pName = p["pName"]

			return pName

		except Exception:
			print("Could not query database")


	'''
	Draws the product chart basis the parameters passed
	'''
	def drawProductChart(self, productRevenues, chartType, xLabel, yLabel, title):
		print(" In draw product chart")
		print("THe chart type passed is:"+ chartType)
		xArr = []
		yArr = []
		for index in range(0, len(productRevenues)):
			prodRev = productRevenues[index]
			xArr.append(prodRev["product"])
			print ("the product is:" + prodRev["product"])
			yArr.append(prodRev["salesRevenue"])
			print ("the product revenue is:" + str(prodRev["salesRevenue"]))


		print ("xArr in create draw Product Chart is:")
		for i in range(0, len(xArr)):
			print ("the product is:" + xArr[i])


		if chartType == Constants.getStrBarChart():
			barChartObj = BarChart(tuple(xArr), yArr)
			barChartObj.setTitle(title)
			barChartObj.setXLabel(xLabel)
			barChartObj.setYLabel(yLabel)
			return barChartObj.drawChart()	        
		elif chartType == Constants.getStrPieChart():
			pieChartObj = PieChart(tuple(xArr), yArr)
			pieChartObj.setTitle(title)
			return pieChartObj.drawChart()
		else:
			print ("there is an error in selecting the correct chart in drawProductChart")
			barChartObj = BarChart(tuple(xArr), yArr)
			barChartObj.setTitle(title)
			barChartObj.setXLabel(xLabel)
			barChartObj.setYLabel(yLabel)
			return barChartObj.drawChart()	        