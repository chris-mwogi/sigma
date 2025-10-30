# sigma/sigma/config/desktop.py
from frappe import _

# Desktop icons configuration for Sigma modules
# Each entry corresponds to a module in modules.txt

module_icons = [
    {
        "module_name": "Sigma Access Control",
        "label": _("Access Control"),
        "icon": "fa fa-user-shield",
        "color": "#3498db",
        "type": "module",
        "link": "List/Sigma Access Control"
    },
    {
        "module_name": "Sigma Case Management",
        "label": _("Case Management"),
        "icon": "fa fa-briefcase",
        "color": "#e67e22",
        "type": "module",
        "link": "List/Case Record"
    },

    {
        "module_name": "Sigma Guard Monitoring",
        "label": _("Guard Monitoring"),
        "icon": "fa fa-user-secret",
        "color": "#e74c3c",
        "type": "module",
        "link": "List/Guard Record"
    },
    {
        "module_name": "Sigma Asset Integrations",
        "label": _("Asset Integrations"),
        "icon": "fa fa-plug",
        "color": "#9b59b6",
        "type": "module",
        "link": "List/Asset Integration"
    },
    {
        "module_name": "Sigma Risk Assessment",
        "label": _("Risk Assessment"),
        "icon": "fa fa-exclamation-triangle",
        "color": "#f1c40f",
        "type": "module",
        "link": "List/Risk Assessment"
    },
    {
        "module_name": "Tracking Dashboard",
        "label": _("Tracking Dashboard"),
        "icon": "fa fa-tachometer-alt",
        "color": "#34495e",
        "type": "page",
        "link": "/app/tracking-dashboard"
    }
]
