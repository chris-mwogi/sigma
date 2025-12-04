# -*- coding: utf-8 -*-
# Copyright (c) 2025, Sigma and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import today, getdate

class VisitorWatchlist(Document):
	"""
	Visitor Watchlist - Security Management
	ISO 27001 A.7.1.1 - Screening of personnel
	Tracks individuals who require additional security screening
	"""
	
	def validate(self):
		"""Validate watchlist entry"""
		# Auto-set added_by to current user
		if not self.added_by:
			self.added_by = frappe.session.user

		self.validate_dates()
		self.check_duplicates()
	
	def validate_dates(self):
		"""Validate expiry date"""
		if self.expiry_date and getdate(self.expiry_date) < getdate(today()):
			frappe.msgprint(_("Expiry date is in the past. Entry will be inactive."))
			self.is_active = 0
	
	def check_duplicates(self):
		"""Check for duplicate entries"""
		existing = frappe.db.exists("Visitor Watchlist", {
			"person_name": self.person_name,
			"id_number": self.id_number,
			"name": ["!=", self.name],
			"is_active": 1
		})
		
		if existing:
			frappe.msgprint(
				_("An active watchlist entry already exists for this person."),
				indicator="orange",
				alert=True
			)
	
	def before_save(self):
		"""Auto-deactivate if expired"""
		if self.expiry_date and getdate(self.expiry_date) < getdate(today()):
			self.is_active = 0
	
	def on_update(self):
		"""Notify security team of watchlist changes"""
		if self.is_active and self.has_value_changed("is_active"):
			self.notify_security_team()
	
	def notify_security_team(self):
		"""Send notification to security team"""
		security_role = frappe.get_all("Has Role",
			filters={"role": "Security Manager"},
			fields=["parent"]
		)

		if security_role:
			recipients = [frappe.db.get_value("User", r.parent, "email") for r in security_role if frappe.db.get_value("User", r.parent, "email")]

			if recipients:
				try:
					frappe.sendmail(
						recipients=recipients,
						subject=f"Watchlist Update: {self.person_name}",
						message=f"""
						<p><strong>Watchlist Entry Updated</strong></p>
						<p><strong>Person:</strong> {self.person_name}</p>
						<p><strong>ID Number:</strong> {self.id_number or 'N/A'}</p>
						<p><strong>Reason:</strong> {self.reason}</p>
						<p><strong>Risk Impact:</strong> {self.risk_score_impact}</p>
						<p><strong>Status:</strong> {'Active' if self.is_active else 'Inactive'}</p>
						<p>Please ensure all security personnel are aware of this entry.</p>
						""",
						reference_doctype="Visitor Watchlist",
						reference_name=self.name
					)
				except Exception as e:
					# Log error but don't fail the transaction
					frappe.log_error(f"Failed to send watchlist notification: {str(e)}", "Watchlist Notification Error")

