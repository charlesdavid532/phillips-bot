import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
from chart import Chart
class BarChart(Chart):
	"""docstring for BarChart"""
	def __init__(self, xArr, yArr):
		super(BarChart, self).__init__(xArr, yArr)

	def setXLabel(self, xLabel):
		self.xLabel = xLabel

	def setYLabel(self, yLabel):
		self.yLabel = yLabel

	def drawChart():
		print("inside draw chart of Bar Chart")

		print ("xArr in create Bar Chart is:")
		for i in range(0, len(self.xArr)):
			print ("the product is:" + self.xArr[i])
			print ("the product revenue is:" + str(self.yArr[i]))

		y_pos = np.arange(len(self.xArr))
		plt.gcf().clear()
		plt.bar(y_pos, self.yArr, align='center')
		plt.xticks(y_pos, self.xArr)
		plt.ylabel(self.yLabel)
		plt.xlabel(self.xLabel)
		plt.title(self.title)

		#Note: TODO:: should be pushed to parent class
		img_data = io.BytesIO()
		plt.savefig(img_data, format='png')
		img_data.seek(0)
		return img_data
		