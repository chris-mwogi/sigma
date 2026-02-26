# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class SLAShortfall(Document):
	"""Child table for SLA Compliance Record - tracks resource shortfalls"""
	
	def validate(self):
		"""Calculate shortfall count"""
		self.shortfall_count = max(0, self.required_count - self.deployed_count)
		
		# Set severity based on shortfall percentage
		if self.required_count > 0:
			shortfall_percentage = (self.shortfall_count / self.required_count) * 100
			if shortfall_percentage >= 75:
				self.severity = "Critical"
			elif shortfall_percentage >= 50:
				self.severity = "High"
			elif shortfall_percentage >= 25:
				self.severity = "Medium"
			else:
				self.severity = "Low"

