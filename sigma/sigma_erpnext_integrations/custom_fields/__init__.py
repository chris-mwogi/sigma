"""
Custom Fields Management for ERPNext Integration

Handles installation and management of custom fields required for integration
"""

import frappe
import json
import os
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def install_custom_fields():
    """
    Install all custom fields required for ERPNext integration
    
    This function should be called during app installation or setup
    """
    # Load custom fields from JSON
    custom_fields_path = os.path.join(
        os.path.dirname(__file__),
        "custom_fields.json"
    )
    
    with open(custom_fields_path, "r") as f:
        custom_fields_data = json.load(f)
    
    # Group custom fields by DocType
    fields_by_doctype = {}
    for field in custom_fields_data:
        dt = field.get("dt")
        if dt not in fields_by_doctype:
            fields_by_doctype[dt] = []
        fields_by_doctype[dt].append(field)
    
    # Create custom fields
    for doctype, fields in fields_by_doctype.items():
        # Check if DocType exists
        if not frappe.db.exists("DocType", doctype):
            print(f"Skipping custom fields for {doctype} - DocType not found")
            continue
        
        print(f"Installing custom fields for {doctype}...")
        
        for field in fields:
            # Check if custom field already exists
            if frappe.db.exists("Custom Field", {
                "dt": doctype,
                "fieldname": field.get("fieldname")
            }):
                print(f"  - {field.get('fieldname')} already exists, skipping")
                continue
            
            try:
                # Create custom field
                custom_field = frappe.get_doc({
                    "doctype": "Custom Field",
                    "dt": field.get("dt"),
                    "fieldname": field.get("fieldname"),
                    "label": field.get("label"),
                    "fieldtype": field.get("fieldtype"),
                    "options": field.get("options"),
                    "insert_after": field.get("insert_after"),
                    "read_only": field.get("read_only", 0),
                    "description": field.get("description"),
                    "default": field.get("default"),
                    "collapsible": field.get("collapsible", 0)
                })
                custom_field.insert(ignore_permissions=True)
                print(f"  ✓ Created {field.get('fieldname')}")
            except Exception as e:
                print(f"  ✗ Error creating {field.get('fieldname')}: {str(e)}")
    
    frappe.db.commit()
    print("Custom fields installation complete!")


def uninstall_custom_fields():
    """
    Remove all custom fields created for ERPNext integration
    
    This function should be called during app uninstallation
    """
    # Load custom fields from JSON
    custom_fields_path = os.path.join(
        os.path.dirname(__file__),
        "custom_fields.json"
    )
    
    with open(custom_fields_path, "r") as f:
        custom_fields_data = json.load(f)
    
    for field in custom_fields_data:
        try:
            if frappe.db.exists("Custom Field", {
                "dt": field.get("dt"),
                "fieldname": field.get("fieldname")
            }):
                frappe.delete_doc("Custom Field", 
                                frappe.db.get_value("Custom Field", {
                                    "dt": field.get("dt"),
                                    "fieldname": field.get("fieldname")
                                }))
                print(f"Removed custom field: {field.get('dt')}.{field.get('fieldname')}")
        except Exception as e:
            print(f"Error removing custom field {field.get('fieldname')}: {str(e)}")
    
    frappe.db.commit()
    print("Custom fields uninstallation complete!")

