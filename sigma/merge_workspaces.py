import frappe

def merge_home_workspaces():
    try:
        sigma = frappe.get_doc("Workspace", "Sigma")
        home = frappe.get_doc("Workspace", "Home")

        home.content = sigma.content
        home.save()

        frappe.delete_doc("Workspace", "Sigma", force=1)
        frappe.db.commit()
        
        print("Successfully merged Home workspaces")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    merge_home_workspaces()