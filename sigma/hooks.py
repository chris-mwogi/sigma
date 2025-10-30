# sigma/sigma/hooks.py
from . import __version__ as app_version

# -----------------------------
# App Metadata
# -----------------------------
app_name = "sigma"
app_title = "Sigma"
app_publisher = "Prismod Technologies Limited"
app_description = "Security Management & Control Systems"
app_email = "info@prismod.co.ke"
app_license = "MIT"
app_version = app_version

# -----------------------------
# Modules and desktop
# -----------------------------
# modules.txt defines all the Python modules to sync
# desktop.py defines how modules appear on ERPNext Desk
# Include all modules
modules = [
    "Sigma Home",
    "Sigma Access Control",
    "Sigma Case Management",
    "Sigma Guard Monitoring",
    "Sigma Asset Integrations",
    "Sigma Risk Assessment",
    "Sigma Visitor Management",
    "sigma Vehicle Management",
    "Sigma ERPNext Integrations"
]

# Desk icon registration
# No global desktop_js here; module icons are configured via config/desktop.py in each module for Frappe 16.
# If using ERPNext 14+, desktop config is automatically picked from config/desktop.py

# -----------------------------
# Documentation
# -----------------------------
# App docs shown in Developer > Documentation
docs = "config/docs.py"

# -----------------------------
# Fixtures
# -----------------------------

fixtures = [
    "Custom Field",
    "Property Setter",
    "Workspace",
    "Role",
    "Client Script",
    {"dt": "Module Def", "filters": [["app_name", "=", "sigma"]]},
    {"dt": "Location Type"},
    {"dt": "Substation Type"},
    {"dt": "Location Subtype"}
]

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "sigma",
# 		"logo": "/assets/sigma/logo.png",
# 		"title": "Sigma",
# 		"route": "/sigma",
# 		"has_permission": "sigma.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/sigma/css/sigma.css"
# app_include_js = "/assets/sigma/js/sigma.js"
app_include_js = []
app_include_css = []

# include js, css files in header of web template
# web_include_css = "/assets/sigma/css/sigma.css"
# web_include_js = "/assets/sigma/js/sigma.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "sigma/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

website_route_rules = [
    {"from_route": "/sigma-home", "to_route": "sigma-home"},
    {"from_route": "/sigma-dashboard", "to_route": "sigma-home"}  # Redirect old URL
]

portal_menu_items = [
    {"title": "Sigma Home", "route": "/sigma-home", "reference_doctype": "Sigma Dashboard"}
]

# include js in page
# page_js = {"page" : "public/js/file.js"}

page_js = {
    "sigma-desk": "public/js/pages/index.js"
}


# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Override Asset tree view with location hierarchy
doctype_tree_js = {
	"Asset": "public/js/asset_tree_override.js"
}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "sigma/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "sigma.utils.jinja_methods",
# 	"filters": "sigma.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "sigma.install.before_install"
after_install = "sigma.sigma_erpnext_integrations.install.after_install"
after_migrate = "sigma.sigma_erpnext_integrations.install.after_migrate"

# Uninstallation
# ------------

# before_uninstall = "sigma.uninstall.before_uninstall"
# after_uninstall = "sigma.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "sigma.utils.before_app_install"
# after_app_install = "sigma.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "sigma.utils.before_app_uninstall"
# after_app_uninstall = "sigma.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "sigma.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Case Record": {
		"on_update": [
			"sigma.api.hooks_automation.auto_escalate_overdue_cases",
			"sigma.api.realtime.RealtimeEvents.emit_case_update_event",
			"sigma.api.realtime.SLAManager.send_escalation_notification",
			"sigma.sigma_erpnext_integrations.api.helpdesk_integration_hooks.sync_case_to_ticket",
			"sigma.sigma_erpnext_integrations.api.projects_integration_hooks.sync_case_to_project",
		],
		"after_insert": [
			"sigma.sigma_erpnext_integrations.api.helpdesk_integration_hooks.sync_case_to_ticket",
			"sigma.sigma_erpnext_integrations.api.projects_integration_hooks.sync_case_to_project",
		],
	},
	"Risk Assessment": {
		"on_update": "sigma.api.hooks_automation.auto_create_mitigation_from_risk",
	},
	"Access Event": {
		"on_insert": [
			"sigma.api.hooks_automation.auto_notify_access_violation",
			"sigma.api.realtime.RealtimeEvents.emit_access_event",
		],
	},
	"Guard Shift": {
		"on_update": "sigma.api.hooks_automation.auto_check_in_guard_shift",
	},
	"Guard Activity": {
		"on_insert": "sigma.api.realtime.RealtimeEvents.emit_guard_location_update",
	},
	"Risk Heatmap": {
		"on_update": "sigma.api.hooks_automation.auto_calculate_risk_score",
	},
	# ERPNext Integration Hooks
	# Using wrapper functions to work with Frappe's hook system
	"Asset": {
		"after_insert": [
			"sigma.sigma_erpnext_integrations.api.stock_integration_hooks.sync_asset_to_item",
			"sigma.sigma_erpnext_integrations.api.support_integration_hooks.sync_asset_maintenance",
		],
		"on_update": [
			"sigma.sigma_erpnext_integrations.api.stock_integration_hooks.sync_asset_to_item",
			"sigma.sigma_erpnext_integrations.api.support_integration_hooks.sync_asset_maintenance",
		],
	},
	"Item": {
		"on_update": "sigma.sigma_erpnext_integrations.api.stock_integration_hooks.sync_item_to_asset",
	},
	"Purchase Receipt": {
		"on_submit": "sigma.sigma_erpnext_integrations.api.buying_integration.BuyingIntegration.create_asset_from_purchase_receipt",
	},
	"Maintenance Visit": {
		"on_submit": "sigma.sigma_erpnext_integrations.api.support_integration_hooks.update_asset_from_maintenance_visit",
		"on_update": "sigma.sigma_erpnext_integrations.api.support_integration_hooks.update_asset_from_maintenance_visit",
	},
	"Incident Report": {
		"after_insert": "sigma.sigma_erpnext_integrations.api.support_integration_hooks.create_maintenance_visit_from_incident",
	},
	"Visitor": {
		"after_insert": "sigma.sigma_erpnext_integrations.api.crm_integration.CRMIntegration.sync_visitor_to_contact",
		"on_update": "sigma.sigma_erpnext_integrations.api.crm_integration.CRMIntegration.sync_visitor_to_contact",
	},
}

# Scheduled Tasks
# ---------------

# Scheduled Tasks
# ---------------

scheduler_events = {
	"hourly": [
		"sigma.api.integrations.refresh_dashboard_cache",
		"sigma.api.integrations.poll_vendor_apis",
		"sigma.sigma_erpnext_integrations.sync_handlers.scheduled_sync.sync_pending_assets",
		"sigma.sigma_erpnext_integrations.sync_handlers.scheduled_sync.sync_maintenance_schedules",
	],
	"daily": [
		"sigma.api.integrations.generate_reports",
		"sigma.sigma_erpnext_integrations.sync_handlers.scheduled_sync.sync_all_integrations",
		"sigma.sigma_erpnext_integrations.sync_handlers.scheduled_sync.cleanup_old_logs",
	],
}

# Testing
# -------

# before_tests = "sigma.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "sigma.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "sigma.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "sigma.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["sigma.utils.before_request"]
# after_request = ["sigma.utils.after_request"]

# Job Events
# ----------
# before_job = ["sigma.utils.before_job"]
# after_job = ["sigma.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"sigma.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

