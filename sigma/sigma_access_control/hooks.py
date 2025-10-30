app_name = "sigma_access_control"
app_title = "Sigma Access Control"
app_publisher = "Sigma"
app_description = "Access control module for Sigma app"
app_icon = "octicon octicon-lock"
app_color = "blue"
app_version = "0.0.1"

app_include_js = ['/assets/sigma_access_control/js/access_control_dashboard.js']

# Doc events
doc_events = {
    "Access Event": {
        "after_insert": "sigma_access_control.sigma_access_control_api.after_access_event_insert",
        "on_update": "sigma_access_control.sigma_access_control_api.on_access_event_update",
        "on_trash": "sigma_access_control.sigma_access_control_api.on_access_event_delete"
    }
}


# Scheduler (placeholder)
scheduler_events = {
    "all": [
        "sigma_access_control.sigma_access_control_api.update_daily_stats"
    ]
}


# Fixtures to export (if any custom fields/property setters are required)
fixtures = [
    "Custom Field",
    "Property Setter"
]