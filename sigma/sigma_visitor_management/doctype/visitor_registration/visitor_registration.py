# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, getdate


class VisitorRegistration(Document):
	"""
	Visitor Registration DocType

	Pre-registration of expected visitors
	ISO 27001 A.6 & A.11 - Physical and logical access control
	ISO 31000 - Risk Management
	DHS/CBP Visitor Management Guidelines
	"""

	def validate(self):
		"""Validate registration"""
		self.validate_visitor()
		self.validate_dates()
		self.validate_host()
		self.check_watchlist()
		self.check_first_time_visitor()
		self.calculate_risk_score()
		self.validate_compliance()
	
	def validate_visitor(self):
		"""Validate visitor exists"""
		if not frappe.db.exists("Visitor", self.visitor):
			frappe.throw(f"Visitor {self.visitor} not found")
	
	def validate_dates(self):
		"""Validate dates"""
		# Convert string dates to date objects for comparison
		arrival_date = getdate(self.expected_arrival_date) if self.expected_arrival_date else None
		if arrival_date and arrival_date < getdate():
			frappe.throw("Expected Arrival Date cannot be in the past")
	
	def validate_host(self):
		"""Validate host employee if specified"""
		if self.host_employee and not frappe.db.exists("Employee", self.host_employee):
			frappe.throw(f"Employee {self.host_employee} not found")

	def check_watchlist(self):
		"""Check if visitor is on watchlist - ISO 27001 A.7.1.1"""
		if not self.visitor:
			return

		# Get visitor details
		visitor = frappe.get_doc("Visitor", self.visitor)

		# Check watchlist by name and ID
		watchlist_entry = frappe.db.exists("Visitor Watchlist", {
			"person_name": f"{visitor.first_name} {visitor.last_name}",
			"is_active": 1
		})

		if not watchlist_entry and visitor.identification_number:
			watchlist_entry = frappe.db.exists("Visitor Watchlist", {
				"id_number": visitor.identification_number,
				"is_active": 1
			})

		if watchlist_entry:
			self.on_watchlist = 1
			self.risk_band = "High"
			frappe.msgprint(
				_("⚠️ WARNING: This visitor is on the security watchlist. Security approval required."),
				indicator="red",
				alert=True
			)
			# Send immediate notification to security
			self.notify_security_watchlist()
		else:
			self.on_watchlist = 0

	def check_first_time_visitor(self):
		"""Check if this is a first-time visitor"""
		if not self.visitor:
			return

		# Count previous registrations for this visitor
		previous_visits = frappe.db.count("Visitor Registration", {
			"visitor": self.visitor,
			"name": ["!=", self.name or ""],
			"status": ["in", ["Confirmed", "Arrived", "Completed"]]
		})

		self.is_first_time_visitor = 1 if previous_visits == 0 else 0

	def calculate_risk_score(self):
		"""Calculate visitor risk score - ISO 31000 Risk Management"""
		risk_score = 0

		# Base risk from visitor type (10 points per risk level)
		visitor_type_weights = {
			"External Visitor": 2,
			"Inter-Station Staff": 1,
			"Contractor": 3,
			"Vendor": 2
		}
		risk_score += visitor_type_weights.get(self.visitor_type, 2) * 10

		# Watchlist adds 30 points (critical risk factor)
		if self.on_watchlist:
			risk_score += 30

		# First-time visitor adds 10 points (unknown entity)
		if self.is_first_time_visitor:
			risk_score += 10

		# Sensitive area access adds 20 points
		if self.access_level in ["Restricted Areas", "Sensitive Areas", "All Areas"]:
			risk_score += 20

		# Unknown company adds 15 points
		if self.visitor:
			visitor = frappe.get_doc("Visitor", self.visitor)
			if not visitor.company_name or visitor.company_name == "Unknown":
				risk_score += 15

		self.risk_score = risk_score

		# Set risk band based on score
		if risk_score >= 60:
			self.risk_band = "High"
		elif risk_score >= 40:
			self.risk_band = "Medium"
		else:
			self.risk_band = "Low"

	def validate_compliance(self):
		"""Validate compliance requirements"""
		# Check NDA requirement
		if self.nda_required and not self.nda_signed:
			frappe.msgprint(
				_("NDA signature is required before visitor can be confirmed."),
				indicator="orange"
			)

		# Check safety induction
		if self.safety_induction_required and not self.safety_induction_completed:
			frappe.msgprint(
				_("Safety induction must be completed before visitor arrival."),
				indicator="orange"
			)

	def before_insert(self):
		"""Set default values"""
		self.registration_date = getdate()
		self.registered_by = frappe.session.user
	
	def on_update(self):
		"""Handle registration updates"""
		# Send notification if status changed
		if self.status == "Confirmed":
			self.send_confirmation_notification()

		# Escalate high-risk visitors to security
		if self.risk_band == "High" and self.has_value_changed("risk_band"):
			self.notify_security_high_risk()

	def notify_security_watchlist(self):
		"""Send immediate notification for watchlist match"""
		try:
			security_role = frappe.get_all("Has Role",
				filters={"role": "Security Manager"},
				fields=["parent"]
			)

			if security_role:
				recipients = []
				for r in security_role:
					email = frappe.db.get_value("User", r.parent, "email")
					if email:
						recipients.append(email)

				if recipients:
					visitor = frappe.get_doc("Visitor", self.visitor)
					frappe.sendmail(
						recipients=recipients,
						subject=f"🚨 WATCHLIST ALERT: {visitor.first_name} {visitor.last_name}",
						message=f"""
						<div style="background-color: #ffebee; padding: 20px; border-left: 5px solid #f44336;">
							<h2 style="color: #c62828;">⚠️ SECURITY WATCHLIST ALERT</h2>
							<p><strong>A visitor on the security watchlist has been registered:</strong></p>
							<ul>
								<li><strong>Visitor:</strong> {visitor.first_name} {visitor.last_name}</li>
								<li><strong>ID Number:</strong> {visitor.identification_number or 'N/A'}</li>
								<li><strong>Company:</strong> {visitor.company_name or 'Unknown'}</li>
								<li><strong>Expected Arrival:</strong> {self.expected_arrival_date} {self.expected_arrival_time or ''}</li>
								<li><strong>Location:</strong> {self.location}</li>
								<li><strong>Host:</strong> {self.host_employee or 'N/A'}</li>
								<li><strong>Purpose:</strong> {self.purpose_of_visit}</li>
								<li><strong>Risk Score:</strong> {self.risk_score}</li>
							</ul>
							<p style="color: #c62828;"><strong>IMMEDIATE ACTION REQUIRED:</strong> Review and approve/reject this registration.</p>
							<p><a href="{frappe.utils.get_url()}/app/visitor-registration/{self.name}" style="background-color: #f44336; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Review Registration</a></p>
						</div>
						""",
						reference_doctype="Visitor Registration",
						reference_name=self.name
					)
		except Exception as e:
			# Log error but don't fail the transaction
			frappe.log_error(f"Failed to send watchlist notification: {str(e)}", "Watchlist Notification Error")

	def notify_security_high_risk(self):
		"""Notify security of high-risk visitor and auto-create case"""
		try:
			# Auto-create case for high-risk visitor
			self.create_security_case()

			security_role = frappe.get_all("Has Role",
				filters={"role": "Security Manager"},
				fields=["parent"]
			)

			if security_role:
				recipients = []
				for r in security_role:
					email = frappe.db.get_value("User", r.parent, "email")
					if email:
						recipients.append(email)

				if recipients:
					visitor = frappe.get_doc("Visitor", self.visitor)
					frappe.sendmail(
						recipients=recipients,
						subject=f"⚠️ HIGH RISK VISITOR: {visitor.first_name} {visitor.last_name}",
						message=f"""
						<div style="background-color: #fff3e0; padding: 20px; border-left: 5px solid #ff9800;">
							<h2 style="color: #e65100;">⚠️ HIGH RISK VISITOR ALERT</h2>
							<p><strong>A high-risk visitor has been registered:</strong></p>
							<ul>
								<li><strong>Visitor:</strong> {visitor.first_name} {visitor.last_name}</li>
								<li><strong>Company:</strong> {visitor.company_name or 'Unknown'}</li>
								<li><strong>Risk Score:</strong> {self.risk_score}</li>
								<li><strong>Risk Band:</strong> {self.risk_band}</li>
								<li><strong>On Watchlist:</strong> {'Yes' if self.on_watchlist else 'No'}</li>
								<li><strong>First Time Visitor:</strong> {'Yes' if self.is_first_time_visitor else 'No'}</li>
								<li><strong>Access Level:</strong> {self.access_level}</li>
								<li><strong>Expected Arrival:</strong> {self.expected_arrival_date}</li>
								<li><strong>Location:</strong> {self.location}</li>
							</ul>
							<p><strong>Please review and approve this registration.</strong></p>
							<p><a href="{frappe.utils.get_url()}/app/visitor-registration/{self.name}" style="background-color: #ff9800; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Review Registration</a></p>
						</div>
						""",
						reference_doctype="Visitor Registration",
						reference_name=self.name
					)
		except Exception as e:
			# Log error but don't fail the transaction
			frappe.log_error(f"Failed to send high-risk notification: {str(e)}", "High Risk Notification Error")

def create_security_case(self):
	"""Auto-create security case for high-risk visitor - ISO 27001 A.11.1.1"""
	try:
		# Check if case already exists for this registration
		existing_case = frappe.db.exists("Case", {
			"linked_visitor": self.visitor,
			"case_type": "Visitor Security Incident",
			"status": ["in", ["Open", "Under Investigation"]]
		})

		if existing_case:
			frappe.msgprint(f"Security case already exists: {existing_case}", alert=True)
			return

		# Get visitor details
		visitor = frappe.get_doc("Visitor", self.visitor)

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
		<h3>High-Risk Visitor Security Alert</h3>
		<p><strong>Auto-generated case for high-risk visitor registration.</strong></p>

		<h4>Visitor Information:</h4>
		<ul>
			<li><strong>Name:</strong> {visitor.first_name} {visitor.last_name}</li>
			<li><strong>Company:</strong> {visitor.company_name or 'Unknown'}</li>
			<li><strong>ID Number:</strong> {visitor.id_number or 'Not provided'}</li>
			<li><strong>Phone:</strong> {visitor.phone_number or 'Not provided'}</li>
			<li><strong>Email:</strong> {visitor.email or 'Not provided'}</li>
		</ul>

		<h4>Risk Assessment:</h4>
		<ul>
			<li><strong>Risk Score:</strong> {self.risk_score}</li>
			<li><strong>Risk Band:</strong> {self.risk_band}</li>
			<li><strong>On Watchlist:</strong> {'Yes' if self.on_watchlist else 'No'}</li>
			<li><strong>First Time Visitor:</strong> {'Yes' if self.is_first_time_visitor else 'No'}</li>
			<li><strong>Visitor Type:</strong> {self.visitor_type}</li>
		</ul>

		<h4>Visit Details:</h4>
		<ul>
			<li><strong>Purpose:</strong> {self.purpose_of_visit}</li>
			<li><strong>Expected Arrival:</strong> {self.expected_arrival_date}</li>
			<li><strong>Location:</strong> {self.location}</li>
			<li><strong>Access Level:</strong> {self.access_level}</li>
			<li><strong>Host Employee:</strong> {self.host_employee or 'Not assigned'}</li>
		</ul>

		<h4>Recommended Actions:</h4>
		<ul>
			<li>Verify visitor identity and credentials</li>
			<li>Review watchlist status and reasons</li>
			<li>Conduct enhanced security screening</li>
			<li>Assign security escort if approved</li>
			<li>Monitor visitor activities during visit</li>
		</ul>

		<p><strong>Registration Reference:</strong> <a href="/app/visitor-registration/{self.name}">{self.name}</a></p>
		"""

		# Create case
		case = frappe.get_doc({
			"doctype": "Case",
			"case_title": f"High-Risk Visitor: {visitor.first_name} {visitor.last_name}",
			"case_type": "Visitor Security Incident",
			"case_category": case_category,
			"case_source": case_source,
			"status": "Open",
			"severity": severity,
			"confidentiality_level": "Restricted",
			"description": description,
			"linked_visitor": self.visitor,
			"date_reported": frappe.utils.today(),
			"assigned_case_manager": frappe.session.user
		})

		case.insert(ignore_permissions=True)
		frappe.db.commit()

		frappe.msgprint(f"Security case created: {case.name}", alert=True, indicator="orange")

	except Exception as e:
		# Log error but don't fail the transaction
		frappe.log_error(f"Failed to create security case: {str(e)}", "Auto Case Creation Error")

	def send_confirmation_notification(self):
		"""Send confirmation notification"""
		try:
			visitor = frappe.get_doc("Visitor", self.visitor)
			if visitor.email:
				frappe.sendmail(
					recipients=[visitor.email],
					subject=f"Visitor Registration Confirmed - {self.location}",
					message=f"""
					Dear {visitor.first_name} {visitor.last_name},

					Your visitor registration has been confirmed for {self.expected_arrival_date}.

					Location: {self.location}
					Expected Arrival Time: {self.expected_arrival_time}
					Purpose: {self.purpose_of_visit}
					Risk Band: {self.risk_band}

					{f"⚠️ Please note: NDA signature is required upon arrival." if self.nda_required else ""}
					{f"⚠️ Please note: Safety induction is required upon arrival." if self.safety_induction_required else ""}
					{f"⚠️ Please note: PPE required - {self.ppe_required}" if self.ppe_required else ""}

					Please arrive on time and check in at the reception.

					Best regards,
					Security Team
					"""
				)
		except Exception as e:
			frappe.log_error(f"Error sending confirmation notification: {str(e)}")
	
	@staticmethod
	def get_pending_registrations(location=None):
		"""Get pending registrations"""
		filters = {"status": "Pending"}
		if location:
			filters["location"] = location
		
		return frappe.get_all(
			"Visitor Registration",
			filters=filters,
			fields=["name", "visitor", "expected_arrival_date", "expected_arrival_time", "location"],
			order_by="expected_arrival_date asc"
		)
	
	@staticmethod
	def get_today_registrations(location=None):
		"""Get registrations for today"""
		today = getdate()
		filters = {
			"expected_arrival_date": today,
			"status": ["in", ["Pending", "Confirmed"]]
		}
		if location:
			filters["location"] = location
		
		return frappe.get_all(
			"Visitor Registration",
			filters=filters,
			fields=["name", "visitor", "expected_arrival_time", "location", "status"],
			order_by="expected_arrival_time asc"
		)
	
	@staticmethod
	def get_overdue_registrations():
		"""Get registrations that haven't been checked in"""
		from frappe.utils import add_days, get_datetime
		
		yesterday = add_days(getdate(), -1)
		
		return frappe.get_all(
			"Visitor Registration",
			filters={
				"expected_arrival_date": ["<=", yesterday],
				"status": ["in", ["Pending", "Confirmed"]]
			},
			fields=["name", "visitor", "expected_arrival_date", "location"],
			order_by="expected_arrival_date asc"
		)

