import frappe
import json

def execute():
    # Fix CRM workspace
    crm_content = [
        {"id": "34f6c0a8-068", "type": "header", "data": {"text": "Sigma CRM", "col": 12}},
        {"id": "4535526d-309", "type": "spacer", "data": {"col": 12}},
        {"id": "533dd8df-a61", "type": "header", "data": {"text": "Quick Actions", "col": 12}},
        {"id": "4cf58a96-dd9", "type": "shortcut", "data": {"name": "Lead", "type": "DocType", "link_to": "Lead", "label": "New Lead"}},
        {"id": "68581b7e-ef6", "type": "shortcut", "data": {"name": "Opportunity", "type": "DocType", "link_to": "Opportunity", "label": "New Opportunity"}},
        {"id": "a272ecca-00d", "type": "shortcut", "data": {"name": "Customer", "type": "DocType", "link_to": "Customer", "label": "New Customer"}},
        {"id": "0c2f5864-43a", "type": "shortcut", "data": {"name": "Contact", "type": "DocType", "link_to": "Contact", "label": "New Contact"}},
        {"id": "6cae2d80-bf6", "type": "spacer", "data": {"col": 12}},
        {"id": "d76b2563-2da", "type": "header", "data": {"text": "Navigation", "col": 12}},
        {"id": "7ff99d4d-e1b", "type": "card", "data": {"card_name": "Lead Management", "col": 4}},
        {"id": "link1", "type": "link", "data": {"name": "Lead", "type": "DocType", "label": "Lead", "link_to": "Lead"}},
        {"id": "link2", "type": "link", "data": {"name": "Lead Source", "type": "DocType", "label": "Lead Source", "link_to": "Lead Source"}},
        {"id": "e480fd5e-722", "type": "card", "data": {"card_name": "Opportunity Management", "col": 4}},
        {"id": "link3", "type": "link", "data": {"name": "Opportunity", "type": "DocType", "label": "Opportunity", "link_to": "Opportunity"}},
        {"id": "link4", "type": "link", "data": {"name": "Opportunity Type", "type": "DocType", "label": "Opportunity Type", "link_to": "Opportunity Type"}},
        {"id": "dc132d56-55a", "type": "card", "data": {"card_name": "Customer Management", "col": 4}},
        {"id": "link5", "type": "link", "data": {"name": "Customer", "type": "DocType", "label": "Customer", "link_to": "Customer"}},
        {"id": "link6", "type": "link", "data": {"name": "Customer Group", "type": "DocType", "label": "Customer Group", "link_to": "Customer Group"}},
        {"id": "link7", "type": "link", "data": {"name": "Contact", "type": "DocType", "label": "Contact", "link_to": "Contact"}}
    ]
    
    crm = frappe.get_doc("Workspace", "CRM")
    crm.content = json.dumps(crm_content)
    crm.save()
    
    # Fix Helpdesk workspace
    helpdesk_content = [
        {"id": "671078cc-ce5", "type": "header", "data": {"text": "Sigma Helpdesk", "col": 12}},
        {"id": "a81065af-673", "type": "spacer", "data": {"col": 12}},
        {"id": "e6f19fce-8ad", "type": "header", "data": {"text": "Quick Actions", "col": 12}},
        {"id": "242f694a-23b", "type": "shortcut", "data": {"name": "HD Ticket", "type": "DocType", "link_to": "HD Ticket", "label": "New Ticket"}},
        {"id": "a0d81f03-87f", "type": "shortcut", "data": {"name": "HD Service Level Agreement", "type": "DocType", "link_to": "HD Service Level Agreement", "label": "New SLA"}},
        {"id": "fb645339-6bd", "type": "shortcut", "data": {"name": "HD Ticket Type", "type": "DocType", "link_to": "HD Ticket Type", "label": "New Ticket Type"}},
        {"id": "ba297996-f98", "type": "shortcut", "data": {"name": "HD Knowledge Base", "type": "DocType", "link_to": "HD Knowledge Base", "label": "Knowledge Base"}},
        {"id": "a8f7b009-02a", "type": "spacer", "data": {"col": 12}},
        {"id": "04e4794c-bc4", "type": "header", "data": {"text": "Navigation", "col": 12}},
        {"id": "4193712a-f61", "type": "card", "data": {"card_name": "Ticket Management", "col": 4}},
        {"id": "link1", "type": "link", "data": {"name": "HD Ticket", "type": "DocType", "label": "Tickets", "link_to": "HD Ticket"}},
        {"id": "link2", "type": "link", "data": {"name": "HD Ticket Type", "type": "DocType", "label": "Ticket Types", "link_to": "HD Ticket Type"}},
        {"id": "link3", "type": "link", "data": {"name": "HD Priority", "type": "DocType", "label": "Priority Levels", "link_to": "HD Priority"}},
        {"id": "a123ab08-741", "type": "card", "data": {"card_name": "Service Level", "col": 4}},
        {"id": "link4", "type": "link", "data": {"name": "HD Service Level Agreement", "type": "DocType", "label": "Service Level Agreements", "link_to": "HD Service Level Agreement"}},
        {"id": "link5", "type": "link", "data": {"name": "HD SLA Status", "type": "DocType", "label": "SLA Status", "link_to": "HD SLA Status"}},
        {"id": "card3", "type": "card", "data": {"card_name": "Knowledge Base", "col": 4}},
        {"id": "link6", "type": "link", "data": {"name": "HD Knowledge Base", "type": "DocType", "label": "Knowledge Base", "link_to": "HD Knowledge Base"}},
        {"id": "link7", "type": "link", "data": {"name": "HD Knowledge Base Category", "type": "DocType", "label": "KB Categories", "link_to": "HD Knowledge Base Category"}}
    ]
    
    helpdesk = frappe.get_doc("Workspace", "Helpdesk")
    helpdesk.content = json.dumps(helpdesk_content)
    helpdesk.save()
    
    # Fix Quality workspace
    quality_content = [
        {"id": "eb7a76dc-38f", "type": "header", "data": {"text": "Sigma Quality", "col": 12}},
        {"id": "70b5e6f5-d7b", "type": "spacer", "data": {"col": 12}},
        {"id": "d277edae-3c5", "type": "header", "data": {"text": "Quick Actions", "col": 12}},
        {"id": "08bc8a7c-a78", "type": "shortcut", "data": {"name": "Quality Inspection", "type": "DocType", "link_to": "Quality Inspection", "label": "New Inspection"}},
        {"id": "2059cd23-dfe", "type": "shortcut", "data": {"name": "Quality Goal", "type": "DocType", "link_to": "Quality Goal", "label": "New Goal"}},
        {"id": "687ceb07-061", "type": "shortcut", "data": {"name": "Quality Review", "type": "DocType", "link_to": "Quality Review", "label": "New Review"}},
        {"id": "d22a3ec9-307", "type": "spacer", "data": {"col": 12}},
        {"id": "d061de98-78d", "type": "header", "data": {"text": "Navigation", "col": 12}},
        {"id": "656d0ca9-c8c", "type": "card", "data": {"card_name": "Quality Inspection", "col": 4}},
        {"id": "link1", "type": "link", "data": {"name": "Quality Inspection", "type": "DocType", "label": "Quality Inspections", "link_to": "Quality Inspection"}},
        {"id": "link2", "type": "link", "data": {"name": "Quality Inspection Template", "type": "DocType", "label": "Inspection Templates", "link_to": "Quality Inspection Template"}},
        {"id": "dce842a0-d53", "type": "card", "data": {"card_name": "Quality Management", "col": 4}},
        {"id": "link3", "type": "link", "data": {"name": "Quality Goal", "type": "DocType", "label": "Quality Goals", "link_to": "Quality Goal"}},
        {"id": "link4", "type": "link", "data": {"name": "Quality Procedure", "type": "DocType", "label": "Quality Procedures", "link_to": "Quality Procedure"}},
        {"id": "link5", "type": "link", "data": {"name": "Quality Review", "type": "DocType", "label": "Quality Reviews", "link_to": "Quality Review"}},
        {"id": "card3", "type": "card", "data": {"card_name": "Reports", "col": 4}},
        {"id": "link6", "type": "link", "data": {"name": "Quality Inspection Summary", "type": "Report", "label": "Inspection Summary", "link_to": "Quality Inspection Summary", "is_query_report": 1}},
        {"id": "link7", "type": "link", "data": {"name": "Quality Goals Progress", "type": "Report", "label": "Goals Progress", "link_to": "Quality Goals Progress", "is_query_report": 1}}
    ]
    
    quality = frappe.get_doc("Workspace", "Quality")
    quality.content = json.dumps(quality_content)
    quality.save()