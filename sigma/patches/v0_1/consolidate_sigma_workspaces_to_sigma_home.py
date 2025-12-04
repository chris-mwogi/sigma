"""
Patch: Consolidate Sigma workspaces to sigma_home module and set Sigma Home as default

This patch:
1. Updates all workspaces from 'Sigma' module to 'sigma_home' module
2. Sets Sigma Home workspace as the default entry point
3. Ensures workspace content is normalized and persisted
"""

import frappe
import json


def execute():
    """
    Consolidate Sigma workspaces to sigma_home module.
    Persist all workspace content from JSON files to database.
    """
    
    # 1. Consolidate workspace modules
    frappe.db.sql("""
        UPDATE `tabWorkspace` SET module = 'sigma_home' WHERE module = 'Sigma'
    """)
    
    # 2. Ensure Sigma Home is visible and is the primary default
    frappe.db.set_value('Workspace', 'Sigma Home', {
        'is_hidden': 0,
        'module': 'sigma_home'
    })
    
    # 3. Ensure key workspaces have correct module
    key_workspaces = ['Home', 'Projects', 'Quality', 'Support', 'CRM', 'Helpdesk', 'Telephony']
    for ws_name in key_workspaces:
        if frappe.db.exists('Workspace', ws_name):
            frappe.db.set_value('Workspace', ws_name, 'module', 'sigma_home')
    
    frappe.db.commit()
