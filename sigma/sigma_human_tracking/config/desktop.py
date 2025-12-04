from frappe import _

def get_data():
    return [
        {
            "module_name": "Sigma Human Tracking",
            "color": "#16a34a",
            "icon": "octicon octicon-location",
            "type": "module",
            "label": _("Sigma Human Tracking"),
        },
        {
            "label": _("Human Tracking Dashboard"),
            "icon": "octicon octicon-pulse",
            "color": "#16a34a",
            "type": "page",
            "link": "human-tracking",
        },
    ]

