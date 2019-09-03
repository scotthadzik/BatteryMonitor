class ReportTime:
	
	def __init__ (self, time, meridian, reported = False):
		self.time = time
		self.meridian = meridian
		self.reported = reported

	def resetReports(self):
		self.reported = False