from frappe import _

def get_data():
    return [
        {
            "module_name": "Sigma Risk Assessment",
            "category": "Modules",
            "label": _("⚠️ Risk Assessment"),
            "color": "red",
            "icon": "alert-triangle",
            "type": "module",
            "description": "Perform and monitor both site and corporate risk assessments."
        }
    ]
