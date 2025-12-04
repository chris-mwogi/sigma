import frappe
import json

def execute():
    workspace = frappe.get_doc('Workspace', 'Sigma Home')
    
    content = [
        {"id": "4ed4464adcd2", "type": "spacer", "data": {"col": 12}},
        {"id": "56d1bd0893d8", "type": "header", "data": {"text": "Quick Actions", "col": 12}},
        
        # Shortcuts section
        {"id": "shortcut1", "type": "shortcut", "data": {"name": "Case", "type": "DocType", "link_to": "Case", "label": "New Case"}},
        {"id": "shortcut2", "type": "shortcut", "data": {"name": "Access Event", "type": "DocType", "link_to": "Access Event", "label": "Record Access"}},
        {"id": "shortcut3", "type": "shortcut", "data": {"name": "Incident Report", "type": "DocType", "link_to": "Incident Report", "label": "Report Incident"}},
        {"id": "shortcut4", "type": "shortcut", "data": {"name": "Guard Shift", "type": "DocType", "link_to": "Guard Shift", "label": "Manage Shifts"}},
        
        {"id": "spacer1", "type": "spacer", "data": {"col": 12}},
        {"id": "header2", "type": "header", "data": {"text": "Dashboard & Reports", "col": 12}},
        
        # Dashboard section
        {"id": "d63348c805be", "type": "card", "data": {"card_name": "Dashboard", "col": 4}},
        {"id": "link1", "type": "link", "data": {"name": "Security Overview", "type": "Dashboard", "link_to": "Security Overview", "label": "Security Dashboard"}},
        {"id": "link2", "type": "link", "data": {"name": "Asset Overview", "type": "Dashboard", "link_to": "Asset Overview", "label": "Asset Dashboard"}},
        
        {"id": "spacer2", "type": "spacer", "data": {"col": 12}},
        {"id": "header3", "type": "header", "data": {"text": "Security Management", "col": 12}},
        
        # Security related cards
        {"id": "8a75a46f98a8", "type": "card", "data": {"card_name": "Case Management", "col": 4}},
        {"id": "link3", "type": "link", "data": {"name": "Case", "type": "DocType", "link_to": "Case", "label": "Cases"}},
        {"id": "link4", "type": "link", "data": {"name": "Case Type", "type": "DocType", "link_to": "Case Type", "label": "Case Types"}},
        
        {"id": "f017edc163a1", "type": "card", "data": {"card_name": "Access Control", "col": 4}},
        {"id": "link5", "type": "link", "data": {"name": "Access Event", "type": "DocType", "link_to": "Access Event", "label": "Access Events"}},
        {"id": "link6", "type": "link", "data": {"name": "Visitor", "type": "DocType", "link_to": "Visitor", "label": "Visitors"}},
        
        {"id": "737baa3a78c8", "type": "card", "data": {"card_name": "Incident Management", "col": 4}},
        {"id": "link7", "type": "link", "data": {"name": "Incident Report", "type": "DocType", "link_to": "Incident Report", "label": "Incident Reports"}},
        {"id": "link8", "type": "link", "data": {"name": "Incident Type", "type": "DocType", "link_to": "Incident Type", "label": "Incident Types"}},
        
        {"id": "spacer3", "type": "spacer", "data": {"col": 12}},
        {"id": "header4", "type": "header", "data": {"text": "Asset & Inventory", "col": 12}},
        
        # Asset related cards
        {"id": "d8bcab0b9f8d", "type": "card", "data": {"card_name": "Asset Management", "col": 4}},
        {"id": "link9", "type": "link", "data": {"name": "Asset", "type": "DocType", "link_to": "Asset", "label": "Assets"}},
        {"id": "link10", "type": "link", "data": {"name": "Asset Category", "type": "DocType", "link_to": "Asset Category", "label": "Asset Categories"}},
        
        {"id": "ba1fb52ce64a", "type": "card", "data": {"card_name": "Asset Maintenance", "col": 4}},
        {"id": "link11", "type": "link", "data": {"name": "Asset Maintenance Log", "type": "DocType", "link_to": "Asset Maintenance Log", "label": "Maintenance Logs"}},
        {"id": "link12", "type": "link", "data": {"name": "Asset Maintenance", "type": "DocType", "link_to": "Asset Maintenance", "label": "Maintenance Schedule"}},
        
        {"id": "spacer4", "type": "spacer", "data": {"col": 12}},
        {"id": "header5", "type": "header", "data": {"text": "Operations", "col": 12}},
        
        # Operations related cards
        {"id": "f8d0482e0fe3", "type": "card", "data": {"card_name": "Guard Management", "col": 4}},
        {"id": "link13", "type": "link", "data": {"name": "Guard Shift", "type": "DocType", "link_to": "Guard Shift", "label": "Guard Shifts"}},
        {"id": "link14", "type": "link", "data": {"name": "Guard", "type": "DocType", "link_to": "Guard", "label": "Guards"}},
        
        {"id": "43019fc8799d", "type": "card", "data": {"card_name": "Contract Management", "col": 4}},
        {"id": "link15", "type": "link", "data": {"name": "Contract", "type": "DocType", "link_to": "Contract", "label": "Contracts"}},
        {"id": "link16", "type": "link", "data": {"name": "Contract Fulfilment Checklist", "type": "DocType", "link_to": "Contract Fulfilment Checklist", "label": "Fulfilment Checklist"}},
        
        {"id": "dc7e2e28d69a", "type": "card", "data": {"card_name": "Location Management", "col": 4}},
        {"id": "link17", "type": "link", "data": {"name": "Location", "type": "DocType", "link_to": "Location", "label": "Locations"}},
        {"id": "link18", "type": "link", "data": {"name": "Location Type", "type": "DocType", "link_to": "Location Type", "label": "Location Types"}},
        
        {"id": "spacer5", "type": "spacer", "data": {"col": 12}},
        {"id": "header6", "type": "header", "data": {"text": "Settings & Configuration", "col": 12}},
        
        # Settings card
        {"id": "6c7c9ccecb36", "type": "card", "data": {"card_name": "System Settings", "col": 4}},
        {"id": "link19", "type": "link", "data": {"name": "Sigma Settings", "type": "DocType", "link_to": "Sigma Settings", "label": "Sigma Settings"}},
        {"id": "link20", "type": "link", "data": {"name": "Naming Series", "type": "DocType", "link_to": "Naming Series", "label": "Naming Series"}}
    ]
    
    workspace.content = json.dumps(content)
    workspace.save()