import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
from chart import Chart
class PieChart(Chart):
	"""docstring for PieChart"""
	def __init__(self, xArr, yArr):
		super(PieChart, self).__init__(xArr, yArr)


	def drawChart(self):
		#labels = 'Python', 'C++', 'Ruby', 'Java'
		#sizes = [215, 130, 245, 210]
		#colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue']
		colors = self.getColorsForPieChart(len(self.yArr))
		#explode = (0.1, 0, 0, 0)  # explode 1st slice
		explode = self.getExplodeForPieChart(len(self.yArr))

		# Plot
		plt.gcf().clear()
		plt.pie(self.yArr, explode=explode, labels=self.xArr, colors=colors,
		        autopct='%1.1f%%', shadow=True, startangle=140)
		 
		plt.axis('equal')
		plt.title(self.title)

		img_data = io.BytesIO()
		plt.savefig(img_data, format='png')
		img_data.seek(0)
		return img_data


	'''
	Returns an array of colors of specified length
	'''
	def getColorsForPieChart(self, length):
	    return self.getColorsList()[:length]

	'''
	Returns an entire list of colors
	'''
	def getColorsList(self):
	    return ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue', 'gray', 'pink', 'purple', 'red']

	'''
	Returns a tuple of explode parameters of specified length
	'''
	def getExplodeForPieChart(self, length):
	    return self.getExplodeTuple()[:length]
	'''
	Returns an entire list of explode tuple
	'''
	def getExplodeTuple(self):
	    return (0.1, 0, 0, 0, 0, 0, 0, 0)
		