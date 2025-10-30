# sigma/sigma/config/docs.py
from frappe import _

# This defines the structure of the app documentation in Frappe

docs = {
    "Sigma": {
        "label": _("Sigma App Documentation"),
        "icon": "fa fa-shield-alt",
        "category": "Modules",
        "type": "module",
        "links": [
            {
                "name": "Access Control",
                "type": "module",
                "link": "/app/sigma-access-control"
            },
            {
                "name": "Call Centre",
                "type": "module",
                "link": "/app/sigma-call-centre"
            },
            {
                "name": "Case Management",
                "type": "module",
                "link": "/app/sigma-case-management"
            },
            {
                "name": "Helpdesk",
                "type": "module",
                "link": "/app/sigma-helpdesk"
            },
            {
                "name": "Guard Monitoring",
                "type": "module",
                "link": "/app/sigma-guard-monitoring"
            },
            {
                "name": "Integrations",
                "type": "module",
                "link": "/app/sigma-integrations"
            },
            {
                "name": "Risk Assessment",
                "type": "module",
                "link": "/app/sigma-risk-assessment"
            },
            {
                "name": "Tracking Dashboard",
                "type": "page",
                "link": "/app/tracking-dashboard"
            }
        ]
    }
}
