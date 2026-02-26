"""Update Risk Management workspace with dashboard shortcuts."""
import frappe


def update_risk_management_workspace():
    """Add dashboard shortcuts to Risk Management workspace."""
    workspace = frappe.get_doc("Workspace", "Risk Management")
    
    # Dashboard shortcuts to add
    dashboard_shortcuts = [
        {"label": "Risk Overview Dashboard", "link_to": "Risk Overview Dashboard", "type": "Dashboard", "color": "blue"},
        {"label": "Risk Register Dashboard", "link_to": "Risk Register Dashboard", "type": "Dashboard", "color": "orange"},
        {"label": "Risk Incident Dashboard", "link_to": "Risk Incident Dashboard", "type": "Dashboard", "color": "red"},
        {"label": "KRI Monitoring Dashboard", "link_to": "KRI Monitoring Dashboard", "type": "Dashboard", "color": "green"},
        {"label": "Risk Treatment Dashboard", "link_to": "Risk Treatment Dashboard", "type": "Dashboard", "color": "purple"},
        {"label": "Risk Control Dashboard", "link_to": "Risk Control Dashboard", "type": "Dashboard", "color": "cyan"},
    ]
    
    # Check which shortcuts already exist
    existing_labels = {s.label for s in workspace.shortcuts}
    
    # Add new dashboard shortcuts
    for shortcut in dashboard_shortcuts:
        if shortcut["label"] not in existing_labels:
            workspace.append("shortcuts", {
                "label": shortcut["label"],
                "link_to": shortcut["link_to"],
                "type": shortcut["type"],
                "color": shortcut["color"],
                "doc_view": ""
            })
            print(f"Added shortcut: {shortcut['label']}")
        else:
            print(f"Shortcut already exists: {shortcut['label']}")
    
    workspace.save()
    frappe.db.commit()
    print("Workspace updated successfully!")


if __name__ == "__main__":
    update_risk_management_workspace()

