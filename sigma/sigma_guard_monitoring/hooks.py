# sigma/sigma/sigma_guard_monitoring/hooks.py
app_name = "sigma_guard_monitoring"
app_title = "Sigma Guard Monitoring"
app_publisher = "Nevel Enterprises Ltd"
app_description = "Security Guarding & Incident Management System integrated with ERPNext Assets"
app_email = "info@nevel.co.ke"
app_license = "MIT"

fixtures = [
    "Custom Field",
    "Custom Role",
    "Workspace",
    "Property Setter"
]

app_name = "sigma_guard_monitoring"

# Portal Menu Items
portal_menu_items = [
    {
        "title": "Guard Monitoring Portal",
        "route": "guard_monitoring_portal",
        "role": "All"  # or "Customer" / "Guard Monitoring Officer"
    }
]

# hooks.py
override_whitelisted_methods = {
    "sigma.sigma_guard_monitoring.www.guard_monitoring_portal.get_context": "sigma_guard_monitoring.www.guard_monitoring_portal.get_context"
}

# Scheduled Tasks
scheduler_events = {
	"daily": [
		"sigma.sigma_guard_monitoring.compliance_scheduler.run_daily_compliance_check"
	]
}

