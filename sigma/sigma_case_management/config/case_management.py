from frappe import _

def get_data():
    return [
        {
            "label": _("Sigma Case Management"),
            "items": [
                {"type": "doctype", "name": "Case", "label": _("Case")},
                {"type": "doctype", "name": "Incident Report", "label": _("Incident Report")},
                {"type": "doctype", "name": "Legal Case", "label": _("Legal Case")},
                {"type": "doctype", "name": "Illegal Connection", "label": _("Illegal Connection")},
                {"type": "page", "name": "case-dashboard", "label": _("Case Dashboard")}
            ]
        }
    ]