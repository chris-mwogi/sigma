# Copyright (c) 2024, Navari Limited and contributors
# For license information, please see license.txt

import frappe

def get_context(context):
	"""Redirect root URL to /app"""
	frappe.local.flags.redirect_location = "/app"
	raise frappe.Redirect

