import frappe
from frappe.website.website_generator import WebsiteGenerator


class SigmaFrontend(WebsiteGenerator):
    """Website page for Sigma Vue frontend"""
    
    def get_context(self, context):
        """Get context for the website page"""
        context.update({
            'title': 'Sigma - Security Management System',
            'description': 'Sigma Security Management System',
            'no_breadcrumbs': True,
        })
        return context

