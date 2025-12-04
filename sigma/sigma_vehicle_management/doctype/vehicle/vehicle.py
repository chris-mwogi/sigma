# Copyright (c) 2025, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today


class Vehicle(Document):
	def validate(self):
		"""Validate vehicle record before saving"""
		self.validate_company_vehicle_fields()
		self.validate_driver_license()
		self.validate_dangerous_goods()
		self.set_default_values()
		self.calculate_risk_score()

	def validate_company_vehicle_fields(self):
		"""Validate company vehicle specific fields"""
		if self.owner_type == "Company Vehicle":
			# Validate assignment type is set
			if not self.assignment_type:
				frappe.throw("Assignment Type is required for Company Vehicles")

			# Validate driver assignment
			if self.assignment_type == "Driver-Assigned" and not self.assigned_to_driver:
				frappe.throw("Assigned to Driver is required for Driver-Assigned vehicles")

			# Validate office assignment
			if self.assignment_type == "Office-Assigned" and not self.assigned_to_office:
				frappe.throw("Assigned to Office/Position is required for Office-Assigned vehicles")

	def validate_driver_license(self):
		"""Validate driver license information - ISO 45001 Compliance"""
		if self.driver_license_expiry:
			expiry_date = getdate(self.driver_license_expiry)
			if expiry_date < getdate(today()):
				frappe.msgprint(
					"⚠️ WARNING: Driver license has expired. Vehicle access may be restricted.",
					indicator="red",
					alert=True
				)

	def validate_dangerous_goods(self):
		"""Validate dangerous goods information - OSHA/IEC Compliance"""
		if self.dangerous_goods_flag and not self.dangerous_goods_class:
			frappe.throw("Dangerous Goods Class is required when carrying dangerous goods")

		if self.cargo_type in ["Dangerous Goods", "Hazardous Materials", "Explosives",
		                       "Flammable", "Chemicals", "Radioactive"]:
			self.dangerous_goods_flag = 1

	def set_default_values(self):
		"""Set default values based on owner type"""
		if self.owner_type == "Company Vehicle":
			# Company vehicles don't require passes by default
			if self.requires_pass is None:
				self.requires_pass = 0
		else:
			# Non-company vehicles require passes by default
			if self.requires_pass is None:
				self.requires_pass = 1

	def calculate_risk_score(self):
		"""Calculate vehicle risk score - ISO 31000 Risk Management"""
		risk_score = 0

		# Base risk from vehicle type (10 points per risk level)
		vehicle_type_weights = {
			"Car": 1,
			"Motorcycle": 2,
			"Truck": 3,
			"Van": 2,
			"Bus": 2,
			"Other": 2
		}
		risk_score += vehicle_type_weights.get(self.vehicle_type, 2) * 10

		# Owner type risk (external entities are higher risk)
		owner_type_weights = {
			"Local Staff": 1,
			"Visiting Staff": 2,
			"External Visitor": 3,
			"Contractor": 3,
			"Vendor": 2,
			"Company Vehicle": 0
		}
		risk_score += owner_type_weights.get(self.owner_type, 2) * 5

		# Blacklisted adds 40 points (critical risk factor)
		if self.is_blacklisted:
			risk_score += 40

		# Dangerous goods adds 30 points (critical risk factor)
		if self.dangerous_goods_flag:
			risk_score += 30

			# Additional risk based on dangerous goods class
			high_risk_classes = ["Class 1 - Explosives", "Class 7 - Radioactive Material"]
			if self.dangerous_goods_class in high_risk_classes:
				risk_score += 20

		# Expired driver license adds 20 points
		if self.driver_license_expiry:
			expiry_date = getdate(self.driver_license_expiry)
			if expiry_date < getdate(today()):
				risk_score += 20

		# Unknown/unverified driver adds 15 points
		if not self.driver_name or not self.driver_license_number:
			risk_score += 15

		# Suspended status adds 25 points
		if self.status == "Suspended":
			risk_score += 25

		self.risk_score = risk_score

		# Set risk band based on score
		if risk_score >= 60:
			self.risk_band = "High"
		elif risk_score >= 40:
			self.risk_band = "Medium"
		else:
			self.risk_band = "Low"

		# Auto-update status for high-risk vehicles
		if self.is_blacklisted and self.status != "Blacklisted":
			self.status = "Blacklisted"

	def after_insert(self):
		"""Actions after vehicle is created"""
		if self.risk_band == "High":
			self.notify_security_high_risk()

	def on_update(self):
		"""Actions after vehicle is updated"""
		# Check if risk band changed to High
		if self.has_value_changed("risk_band") and self.risk_band == "High":
			self.notify_security_high_risk()

	def notify_security_high_risk(self):
		"""Notify security of high-risk vehicle and auto-create case"""
		try:
			# Auto-create case for high-risk vehicle
			self.create_security_case()

			security_role = frappe.get_all("Has Role",
				filters={"role": "Security Manager"},
				fields=["parent"]
			)

			if security_role:
				recipients = [frappe.db.get_value("User", r.parent, "email")
				             for r in security_role
				             if frappe.db.get_value("User", r.parent, "email")]

				if recipients:
					frappe.sendmail(
						recipients=recipients,
						subject=f"⚠️ High-Risk Vehicle Alert: {self.license_plate}",
						message=f"""
						<h3>High-Risk Vehicle Detected</h3>
						<p><strong>License Plate:</strong> {self.license_plate}</p>
						<p><strong>Vehicle Type:</strong> {self.vehicle_type}</p>
						<p><strong>Owner Type:</strong> {self.owner_type}</p>
						<p><strong>Risk Score:</strong> {self.risk_score}</p>
						<p><strong>Risk Band:</strong> {self.risk_band}</p>
						<p><strong>Blacklisted:</strong> {'Yes' if self.is_blacklisted else 'No'}</p>
						<p><strong>Dangerous Goods:</strong> {'Yes' if self.dangerous_goods_flag else 'No'}</p>
						<p><strong>Driver:</strong> {self.driver_name or 'Unknown'}</p>
						<p><strong>Action Required:</strong> Enhanced security screening required</p>
						<p><a href="{frappe.utils.get_url()}/app/vehicle/{self.name}">View Vehicle Record</a></p>
						""",
						reference_doctype="Vehicle",
						reference_name=self.name
					)
		except Exception as e:
			# Log error but don't fail the transaction
			frappe.log_error(f"Failed to send high-risk vehicle notification: {str(e)}",
			                "High Risk Vehicle Notification Error")

	def create_security_case(self):
		"""Auto-create security case for high-risk vehicle - ISO 27001 A.11.1.1"""
		try:
			# Check if case already exists for this vehicle
			existing_case = frappe.db.exists("Case", {
				"linked_vehicle": self.name,
				"case_type": "Vehicle Security Incident",
				"status": ["in", ["Open", "Under Investigation"]]
			})

			if existing_case:
				frappe.msgprint(f"Security case already exists: {existing_case}", alert=True)
				return

			# Determine severity based on risk score
			if self.risk_score >= 80:
				severity = "Critical"
			elif self.risk_score >= 60:
				severity = "High"
			else:
				severity = "Medium"

			# Get case category and source
			case_category = frappe.db.get_value("Case Category", {"category_code": "SEC"}, "name")
			if not case_category:
				case_category = frappe.db.get_value("Case Category", {}, "name")  # Get any category

			case_source = frappe.db.get_value("Case Source", {"source_name": "Security Alert"}, "name")
			if not case_source:
				case_source = frappe.db.get_value("Case Source", {}, "name")  # Get any source

			# Build case description
			description = f"""
			<h3>High-Risk Vehicle Security Alert</h3>
			<p><strong>Auto-generated case for high-risk vehicle detection.</strong></p>

			<h4>Vehicle Information:</h4>
			<ul>
				<li><strong>License Plate:</strong> {self.license_plate}</li>
				<li><strong>Vehicle Type:</strong> {self.vehicle_type}</li>
				<li><strong>Make/Model:</strong> {self.make or 'Unknown'} {self.model or ''}</li>
				<li><strong>Color:</strong> {self.color or 'Not specified'}</li>
				<li><strong>Owner Type:</strong> {self.owner_type}</li>
				<li><strong>Owner Name:</strong> {self.owner_name or 'Not specified'}</li>
			</ul>

			<h4>Risk Assessment:</h4>
			<ul>
				<li><strong>Risk Score:</strong> {self.risk_score}</li>
				<li><strong>Risk Band:</strong> {self.risk_band}</li>
				<li><strong>Blacklisted:</strong> {'Yes - ' + (self.blacklist_reason or 'No reason provided') if self.is_blacklisted else 'No'}</li>
				<li><strong>Dangerous Goods:</strong> {'Yes - ' + (self.dangerous_goods_class or 'Class not specified') if self.dangerous_goods_flag else 'No'}</li>
				<li><strong>Cargo Type:</strong> {self.cargo_type or 'Not specified'}</li>
			</ul>

			<h4>Driver Information:</h4>
			<ul>
				<li><strong>Driver Name:</strong> {self.driver_name or 'Unknown'}</li>
				<li><strong>License Number:</strong> {self.driver_license_number or 'Not provided'}</li>
				<li><strong>License Expiry:</strong> {self.driver_license_expiry or 'Not provided'}</li>
				<li><strong>Contact:</strong> {self.driver_contact or 'Not provided'}</li>
			</ul>

			<h4>Recommended Actions:</h4>
			<ul>
				<li>Verify vehicle registration and ownership</li>
				<li>Conduct enhanced security screening</li>
				<li>Verify driver identity and license validity</li>
				{"<li><strong>CRITICAL:</strong> Review blacklist status and reasons</li>" if self.is_blacklisted else ""}
				{"<li><strong>CRITICAL:</strong> Verify dangerous goods permits and safety compliance</li>" if self.dangerous_goods_flag else ""}
				<li>Inspect vehicle cargo if applicable</li>
				<li>Assign security escort if approved for entry</li>
			</ul>

			<p><strong>Vehicle Record:</strong> <a href="/app/vehicle/{self.name}">{self.name}</a></p>
			"""

			# Create case
			case = frappe.get_doc({
				"doctype": "Case",
				"case_title": f"High-Risk Vehicle: {self.license_plate}",
				"case_type": "Vehicle Security Incident",
				"case_category": case_category,
				"case_source": case_source,
				"status": "Open",
				"severity": severity,
				"confidentiality_level": "Restricted",
				"description": description,
				"linked_vehicle": self.name,
				"date_reported": frappe.utils.today(),
				"assigned_case_manager": frappe.session.user
			})

			case.insert(ignore_permissions=True)
			frappe.db.commit()

			frappe.msgprint(f"Security case created: {case.name}", alert=True, indicator="orange")

		except Exception as e:
			# Log error but don't fail the transaction
			frappe.log_error(f"Failed to create security case: {str(e)}", "Auto Case Creation Error")

