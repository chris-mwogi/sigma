"""
Sigma Frontend Route Handler

This module handles the /sigma-frontend route and serves the Vue.js frontend application.
The frontend is a standalone single-page application (SPA) that communicates with the
Frappe backend API.
"""

import frappe
from frappe.website.website_generator import WebsiteGenerator


def get_context(context):
    """
    Get context for the Sigma frontend page.

    This function is called by Frappe when rendering the sigma-frontend.html template.
    It prepares the context data needed for the frontend application.
    """
    # Get current user information
    context.user = frappe.session.user
    context.user_full_name = frappe.db.get_value("User", frappe.session.user, "full_name")

    # Get user roles
    context.user_roles = frappe.get_roles(frappe.session.user)

    # Get CSRF token for frontend API calls
    context.csrf_token = frappe.sessions.get_csrf_token()

    # Get app version
    try:
        from sigma import __version__
        context.app_version = __version__
    except:
        context.app_version = "0.0.1"

    # Set page title
    context.page_title = "Sigma - Security Management System"

    # Disable standard Frappe page elements
    context.no_cache = 1

    return context

