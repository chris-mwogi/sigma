"""
Installation and Setup Scripts for Sigma ERPNext Integrations
"""

import frappe
from frappe import _


def after_install():
    """
    Run after app installation
    
    - Install custom fields
    - Create default settings
    - Setup integration configuration
    """
    print("\n" + "="*60)
    print("Installing Sigma ERPNext Integrations...")
    print("="*60 + "\n")
    
    # Check if ERPNext is installed
    if "erpnext" not in frappe.get_installed_apps():
        print("⚠️  WARNING: ERPNext is not installed!")
        print("   Some integrations will not be available.")
        print("   Please install ERPNext to enable full integration.\n")
    else:
        print("✓ ERPNext detected\n")
    
    # Check if Helpdesk is installed
    if "helpdesk" in frappe.get_installed_apps():
        print("✓ Frappe Helpdesk detected\n")
    else:
        print("ℹ️  Frappe Helpdesk not installed")
        print("   Helpdesk integration will not be available.\n")
    
    # Install custom fields
    print("Installing custom fields...")
    try:
        from sigma.sigma_erpnext_integrations.custom_fields import install_custom_fields
        install_custom_fields()
        print("✓ Custom fields installed\n")
    except Exception as e:
        print(f"✗ Error installing custom fields: {str(e)}\n")
        frappe.log_error("Custom Fields Installation Error", str(e))
    
    # Create default Integration Settings
    print("Creating default integration settings...")
    try:
        if not frappe.db.exists("Sigma Integration Settings", "Sigma Integration Settings"):
            settings = frappe.get_doc({
                "doctype": "Sigma Integration Settings",
                "enable_stock_integration": 1,
                "enable_buying_integration": 1,
                "enable_selling_integration": 1,
                "enable_support_integration": 1,
                "enable_crm_integration": 1,
                "enable_projects_integration": 1,
                "enable_helpdesk_integration": 1,
                "auto_sync": 1,
                "sync_interval": 3600
            })
            settings.insert(ignore_permissions=True)
            print("✓ Integration settings created\n")
        else:
            print("ℹ️  Integration settings already exist\n")
    except Exception as e:
        print(f"✗ Error creating settings: {str(e)}\n")
        frappe.log_error("Integration Settings Creation Error", str(e))
    
    # Create Security Assets item group if it doesn't exist
    if "erpnext" in frappe.get_installed_apps():
        print("Setting up Item Groups...")
        try:
            if not frappe.db.exists("Item Group", "Security Assets"):
                item_group = frappe.get_doc({
                    "doctype": "Item Group",
                    "item_group_name": "Security Assets",
                    "parent_item_group": "All Item Groups",
                    "is_group": 0
                })
                item_group.insert(ignore_permissions=True)
                print("✓ Security Assets item group created\n")
            else:
                print("ℹ️  Security Assets item group already exists\n")
        except Exception as e:
            print(f"✗ Error creating item group: {str(e)}\n")
    
    frappe.db.commit()
    
    print("="*60)
    print("✓ Sigma ERPNext Integrations installed successfully!")
    print("="*60 + "\n")
    
    print("Next Steps:")
    print("1. Configure integration settings in: Setup > Sigma Integration Settings")
    print("2. Review custom fields added to ERPNext DocTypes")
    print("3. Test integration by creating a new Asset\n")


def after_migrate():
    """
    Run after database migration
    
    - Update custom fields if needed
    - Migrate data if schema changed
    """
    print("Running post-migration tasks for Sigma ERPNext Integrations...")
    
    # Reinstall custom fields to catch any updates
    try:
        from sigma.sigma_erpnext_integrations.custom_fields import install_custom_fields
        install_custom_fields()
        print("✓ Custom fields updated")
    except Exception as e:
        print(f"✗ Error updating custom fields: {str(e)}")
        frappe.log_error("Custom Fields Update Error", str(e))
    
    frappe.db.commit()


def before_uninstall():
    """
    Run before app uninstallation
    
    - Remove custom fields
    - Clean up integration data
    """
    print("\n" + "="*60)
    print("Uninstalling Sigma ERPNext Integrations...")
    print("="*60 + "\n")
    
    # Ask for confirmation
    print("⚠️  WARNING: This will remove all custom fields and integration data!")
    print("   Integration logs will be preserved.\n")
    
    # Remove custom fields
    print("Removing custom fields...")
    try:
        from sigma.sigma_erpnext_integrations.custom_fields import uninstall_custom_fields
        uninstall_custom_fields()
        print("✓ Custom fields removed\n")
    except Exception as e:
        print(f"✗ Error removing custom fields: {str(e)}\n")
        frappe.log_error("Custom Fields Removal Error", str(e))
    
    frappe.db.commit()
    
    print("="*60)
    print("✓ Sigma ERPNext Integrations uninstalled")
    print("="*60 + "\n")

