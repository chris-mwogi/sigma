import frappe
import json

def execute():
    # Update Risk Assessment workspace
    risk_content = [
        {"id": "b1aa20cbcf47", "type": "header", "data": {"text": "Risk Assessment Overview"}},
        {"id": "b2aa20cbcf48", "type": "shortcut", "data": {"name": "Risk Assessment", "type": "DocType", "link_to": "Risk Assessment", "label": "Risk Assessment"}},
        {"id": "b3aa20cbcf49", "type": "shortcut", "data": {"name": "Risk Matrix", "type": "DocType", "link_to": "Risk Matrix", "label": "Risk Matrix"}},
        {"id": "b4aa20cbcf50", "type": "shortcut", "data": {"name": "Risk Category", "type": "DocType", "link_to": "Risk Category", "label": "Risk Category"}},
        {"id": "b5aa20cbcf51", "type": "spacer", "data": {"col": 12}},
        {"id": "b6aa20cbcf52", "type": "card", "data": {"card_name": "Risk Reports", "col": 4}},
        {"id": "b7aa20cbcf53", "type": "link", "data": {"name": "Risk Assessment Report", "type": "Report", "label": "Risk Assessment Report", "link_to": "Risk Assessment Report", "is_query_report": 1}},
        {"id": "b8aa20cbcf54", "type": "link", "data": {"name": "Risk Matrix Report", "type": "Report", "label": "Risk Matrix Report", "link_to": "Risk Matrix Report", "is_query_report": 1}}
    ]
    
    risk_ws = frappe.get_doc('Workspace', 'Risk Assessment')
    risk_ws.content = json.dumps(risk_content)
    risk_ws.save()
    
    # Update Assets & Inventory workspace
    assets_content = [
        {"id": "a1aa20cbcf47", "type": "header", "data": {"text": "Assets & Inventory Overview"}},
        {"id": "a2aa20cbcf48", "type": "shortcut", "data": {"name": "Asset", "type": "DocType", "link_to": "Asset", "label": "Asset"}},
        {"id": "a3aa20cbcf49", "type": "shortcut", "data": {"name": "Asset Category", "type": "DocType", "link_to": "Asset Category", "label": "Asset Category"}},
        {"id": "a4aa20cbcf50", "type": "shortcut", "data": {"name": "Asset Movement", "type": "DocType", "link_to": "Asset Movement", "label": "Asset Movement"}},
        {"id": "a5aa20cbcf51", "type": "spacer", "data": {"col": 12}},
        {"id": "a6aa20cbcf52", "type": "card", "data": {"card_name": "Asset Reports", "col": 4}},
        {"id": "a7aa20cbcf53", "type": "link", "data": {"name": "Asset Movement Report", "type": "Report", "label": "Asset Movement Report", "link_to": "Asset Movement Report", "is_query_report": 1}},
        {"id": "a8aa20cbcf54", "type": "link", "data": {"name": "Asset Depreciation Report", "type": "Report", "label": "Asset Depreciation Report", "link_to": "Asset Depreciation Report", "is_query_report": 1}}
    ]
    
    assets_ws = frappe.get_doc('Workspace', 'Assets & Inventory')
    assets_ws.content = json.dumps(assets_content)
    assets_ws.save()