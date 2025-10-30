from frappe import _

# Optional: adds module desktop link
def get_data():
    return [
        {
            "module_name": "Sigma Case Management",
            "color": "green",
            "icon": "octicon octicon-shield",
            "type": "module",
            "label": _("Sigma Case Management"),
            "link": "/cases"  # Portal page route
        }
    ]
