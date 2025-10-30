app_name = "sigma_asset_integrations"
app_title = "Sigma Asset Integrations"
app_publisher = "Prismod Technologies Limited"
app_description = "Integrations for IoT, OpManager, and unified asset telemetry"
app_email = "support@prismod.co.ke"
app_license = "MIT"

portal_menu_items = [
    {
        "title": "Tracking Dashboard",
        "route": "/tracking-dashboard",
        "reference_doctype": None,
        "icon": "fa fa-map-marker-alt"
    }
]

# Include page and api
app_include_js = [
    "/assets/sigma_asset_integrations/js/tracking_dashboard.js"
]

fixtures = [
    {
        "dt": "Property Setter",
        "filters": [["name", "in", [
            "Asset-custom_last_seen",
            "Asset-custom_last_known_location",
            "Asset-custom_tracker_mode",
            "Asset Category-custom_category_icon"
        ]]]
    },
    {
        "dt": "Custom Field",
        "filters": [["dt", "in", ["Asset", "Asset Category"]]]
    },
    {
        "dt": "Workspace",
        "filters": [["module", "=", "Sigma Asset Integrations"]]
    },
]

# Map portal route to function
app_name = "sigma_asset_integrations"
app_include_js = ["/assets/sigma/js/tracking-dashboard.js"]

# Website route for portal page
website_generators = ["Tracking Dashboard"]  # Optional if using Frappe Web Page

# Asset DocType Hooks
doc_events = {
	"Asset": {
		"before_insert": "sigma.sigma_asset_integrations.asset_hooks.auto_generate_serial_number",
		"before_save": [
			"sigma.sigma_asset_integrations.asset_hooks.auto_generate_serial_number",
			"sigma.sigma_asset_integrations.asset_hooks.validate_gps_coordinates",
			"sigma.sigma_asset_integrations.asset_hooks.validate_parent_system"
		]
	}
}
