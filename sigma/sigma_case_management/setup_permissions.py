# -*- coding: utf-8 -*-
# Copyright (c) 2025, Sigma and contributors
# For license information, please see license.txt

"""
Case Management Role-Based Access Control Setup
Configures permissions for all Case Management DocTypes
"""

import frappe
from frappe import _


def setup_case_management_roles():
    """Create all required roles for Case Management"""
    
    roles = [
        {
            "role_name": "Case Manager",
            "desk_access": 1,
            "description": "Full access to manage all cases and investigations"
        },
        {
            "role_name": "Case Intake Officer",
            "desk_access": 1,
            "description": "Create and triage new cases"
        },
        {
            "role_name": "Investigator",
            "desk_access": 1,
            "description": "Conduct investigations and manage evidence"
        },
        {
            "role_name": "Ethics Officer",
            "desk_access": 1,
            "description": "Review compliance and ethical matters"
        },
        {
            "role_name": "Legal Officer",
            "desk_access": 1,
            "description": "Legal review and compliance oversight"
        },
        {
            "role_name": "Case Viewer",
            "desk_access": 1,
            "description": "View assigned cases only"
        }
    ]
    
    for role_data in roles:
        if not frappe.db.exists("Role", role_data["role_name"]):
            role = frappe.get_doc({
                "doctype": "Role",
                "role_name": role_data["role_name"],
                "desk_access": role_data["desk_access"],
                "description": role_data.get("description", "")
            })
            role.insert(ignore_permissions=True)
            print(f"✓ Created role: {role_data['role_name']}")
        else:
            print(f"  Role already exists: {role_data['role_name']}")


def setup_case_permissions():
    """Configure permissions for Case DocType"""
    
    permissions = [
        # System Manager - Full access
        {
            "role": "System Manager",
            "permlevel": 0,
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "submit": 1,
            "cancel": 1,
            "amend": 1,
            "report": 1,
            "export": 1,
            "import": 1,
            "share": 1,
            "print": 1,
            "email": 1
        },
        # Case Manager - Full operational access
        {
            "role": "Case Manager",
            "permlevel": 0,
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "submit": 1,
            "cancel": 1,
            "amend": 1,
            "report": 1,
            "export": 1,
            "share": 1,
            "print": 1,
            "email": 1
        },
        # Case Intake Officer - Create and edit
        {
            "role": "Case Intake Officer",
            "permlevel": 0,
            "read": 1,
            "write": 1,
            "create": 1,
            "submit": 1,
            "report": 1,
            "print": 1,
            "email": 1
        },
        # Investigator - Read and update
        {
            "role": "Investigator",
            "permlevel": 0,
            "read": 1,
            "write": 1,
            "report": 1,
            "print": 1,
            "email": 1
        },
        # Ethics Officer - Read and review
        {
            "role": "Ethics Officer",
            "permlevel": 0,
            "read": 1,
            "write": 1,
            "report": 1,
            "print": 1,
            "email": 1
        },
        # Legal Officer - Read and review
        {
            "role": "Legal Officer",
            "permlevel": 0,
            "read": 1,
            "write": 1,
            "report": 1,
            "print": 1,
            "email": 1
        },
        # Case Viewer - Read only
        {
            "role": "Case Viewer",
            "permlevel": 0,
            "read": 1,
            "report": 1,
            "print": 1
        }
    ]
    
    apply_permissions("Case", permissions)


def apply_permissions(doctype, permissions):
    """Apply permissions to a DocType"""
    
    # Clear existing custom permissions
    frappe.db.delete("Custom DocPerm", {"parent": doctype})
    
    for perm in permissions:
        perm_doc = frappe.get_doc({
            "doctype": "Custom DocPerm",
            "parent": doctype,
            "parenttype": "DocType",
            "parentfield": "permissions",
            **perm
        })
        perm_doc.insert(ignore_permissions=True)
    
    frappe.db.commit()
    print(f"✓ Applied permissions for {doctype}")

