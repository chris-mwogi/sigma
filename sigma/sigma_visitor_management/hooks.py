# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

app_name = "sigma"
app_title = "Sigma Visitor Management"
app_publisher = "Frappe Technologies Pvt. Ltd."
app_description = "Comprehensive Visitor Management System with VMS Integration"
app_icon = "icon-users"
app_color = "#4CAF50"
app_email = "support@frappe.io"
app_license = "MIT"
app_version = "1.0.0"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = [
	"sigma_visitor_management/public/css/visitor_management.css"
]
app_include_js = [
	"sigma_visitor_management/public/js/visitor_management.js"
]

# include js, css files in header of web template
# web_include_css = "/assets/sigma_visitor_management/css/visitor_management.css"
# web_include_js = "/assets/sigma_visitor_management/js/visitor_management.js"

# include custom scss in every page
# page_js = {"page": "public/js/file.js"}
# page_css = {"page": "public/css/file.css"}

# include js in page
# page_js = {"page": "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Home)
# home_page = "Redirecting to Frappe"

# website user home page (by default, standard page will be rendered)
# website_user_home_page = "Redirecting to Frappe"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# -----

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "sigma_visitor_management.utils.jinja_methods",
# 	"filters": "sigma_visitor_management.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "sigma_visitor_management.install.before_install"
# after_install = "sigma_visitor_management.install.after_install"

# Uninstallation
# ---------------

# before_uninstall = "sigma_visitor_management.uninstall.before_uninstall"
# after_uninstall = "sigma_visitor_management.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps

# before_app_publish = "sigma_visitor_management.api.before_app_publish"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "sigma_visitor_management.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype_tree.get_permission_query_conditions",
# }

# has_permission = {
# 	"Event": "frappe.desk.doctype_tree.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_submit": "method",
# 		"on_cancel": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
	"daily": [
		"sigma.sigma_visitor_management.scheduler.daily_visitor_cleanup",
		"sigma.sigma_visitor_management.scheduler.daily_vms_sync"
	],
	"hourly": [
		"sigma.sigma_visitor_management.scheduler.hourly_vms_event_sync"
	]
}

# Testing
# -------

# before_tests = "sigma_visitor_management.install.before_tests"

# Overrides
# ---------

# Document methods
# override_whitelisted_methods = {
# 	"frappe.client.get_list": "sigma_visitor_management.api.get_list"
# }

# Classes
# override_whitelisted_classes = {
# 	"frappe.widgets.query_report.QueryReport": "custom_app.query_report.QueryReport"
# }

# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_field}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_field}",
		# redact common fields
		"redact_fields": ["name", "owner", "modified_by"],
	},
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"sigma_visitor_management.auth.validate_auth"
# ]

# API Routes
# ----------

# api_routes = {
# 	"api/method/sigma_visitor_management.api.visitor_api.register_visitor": "sigma_visitor_management.api.visitor_api.register_visitor",
# }

# Fixtures
# --------

fixtures = [
	"Custom Role",
	"Custom Field",
	"Property Setter"
]

# Migrate from Phase 4
# --------------------

# Migration hooks
# migrate_from_phase4 = "sigma.sigma_visitor_management.migrations.migrate_phase4_to_phase6"

