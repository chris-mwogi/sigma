# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PatrolCheckpoint(Document):
	"""
	Defines patrol checkpoints within a location.
	
	Each checkpoint has GPS coordinates, required resources, and a QR code
	for mobile app verification.
	"""

	def validate(self):
		"""Validate patrol checkpoint data"""
		self.validate_location()
		self.validate_gps_coordinates()

	def validate_location(self):
		"""Ensure location exists"""
		if not frappe.db.exists("Location", self.location):
			frappe.throw(f"Location {self.location} does not exist")

	def validate_gps_coordinates(self):
		"""Validate GPS coordinates if provided"""
		if self.gps_latitude:
			if not (-90 <= self.gps_latitude <= 90):
				frappe.throw("GPS Latitude must be between -90 and 90")
		
		if self.gps_longitude:
			if not (-180 <= self.gps_longitude <= 180):
				frappe.throw("GPS Longitude must be between -180 and 180")

	def on_update(self):
		"""Generate QR code if not already present"""
		if not self.qr_code and self.name:
			self.generate_qr_code()

	def generate_qr_code(self):
		"""Generate QR code for checkpoint"""
		try:
			import qrcode
			import io
			from PIL import Image
			
			# Create QR code data
			qr_data = f"CHECKPOINT:{self.name}|LOCATION:{self.location}|GPS:{self.gps_latitude},{self.gps_longitude}"
			
			# Generate QR code
			qr = qrcode.QRCode(version=1, box_size=10, border=5)
			qr.add_data(qr_data)
			qr.make(fit=True)
			
			img = qr.make_image(fill_color="black", back_color="white")
			
			# Save to file
			img_io = io.BytesIO()
			img.save(img_io, format='PNG')
			img_io.seek(0)
			
			# Attach to document
			from frappe.utils.file_manager import save_file
			file_name = f"qr_code_{self.name}.png"
			save_file(file_name, img_io.getvalue(), "Patrol Checkpoint", self.name)
			
		except Exception as e:
			frappe.log_error(f"Failed to generate QR code: {str(e)}")

