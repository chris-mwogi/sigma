from frappe import _

def get_data():
    return [
        {
            "module_name": "Sigma Assets",
            "color": "#007bff",
            "icon": "octicon octicon-briefcase",
            "type": "module",
            "label": _("Sigma Assets"),
        },
        {
            "label": _("Asset Tracking Dashboard"),
            "icon": "octicon octicon-location",
            "color": "#16a34a",
            "type": "page",
            "link": "tracking-dashboard",
        },
    ]

