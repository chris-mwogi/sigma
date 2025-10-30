from frappe import _

def get_data():
    return [
        {
            "module_name": "Sigma Integrations",
            "color": "#2563eb",
            "icon": "octicon octicon-plug",
            "type": "module",
            "label": _("Sigma Integrations"),
        },
        {
            "label": _("Unified Asset Tracking"),
            "icon": "octicon octicon-location",
            "color": "#16a34a",
            "type": "page",
            "link": "tracking-dashboard",
        },
    ]
