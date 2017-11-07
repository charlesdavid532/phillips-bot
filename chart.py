class Chart(object):
	"""docstring for Chart"""
	def __init__(self, xArr, yArr):
		super(Chart, self).__init__()
		self.xArr = xArr
		self.yArr = yArr

	def setTitle(self, title):
		self.title = title

	def drawChart(self):
		print("inside draw chart of Chart")
		pass
		