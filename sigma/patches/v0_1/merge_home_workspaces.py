import frappe

def execute():
    # Check if Sigma Home workspace exists
    if not frappe.db.exists("Workspace", "Sigma Home"):
        # Sigma Home doesn't exist, so skip this patch
        return

    # Get both workspaces
    sigma_home = frappe.get_doc("Workspace", "Sigma Home")
    home = frappe.get_doc("Workspace", "Home")

    # Update Home with Sigma Home's content and settings
    home.content = sigma_home.content
    home.public = sigma_home.public
    home.for_user = sigma_home.for_user
    home.parent_page = sigma_home.parent_page
    home.sequence_id = sigma_home.sequence_id
    home.is_hidden = sigma_home.is_hidden
    home.title = "Home"  # Keep the title as Home
    home.icon = "home"   # Set home icon
    home.onboarding = "Sigma"
    home.extends = None
    home.extends_another_page = 0
    home.is_default = 1
    home.is_standard = 1
    home.developer_mode_only = 0
    home.disable_user_customization = 0

    # Save Home workspace
    home.save()

    # Delete Sigma Home workspace
    frappe.delete_doc("Workspace", "Sigma Home", force=1)