"""
Sigma setup helpers that can be invoked via:
  bench --site prismod.localhost execute sigma.api.setup_integration.create_page
  bench --site prismod.localhost execute sigma.api.setup_integration.create_customizations
  bench --site prismod.localhost execute sigma.api.setup_integration.create_dashboard_charts
"""

import json
import frappe
from frappe.utils import getdate, now_datetime, add_days


def _ensure_child_doctype_asset_ip():
    if frappe.db.exists('DocType', 'Asset IP Address'):
        return 'exists'
    dt = frappe.new_doc('DocType')
    dt.name = 'Asset IP Address'
    dt.module = 'Sigma Asset Integrations'
    dt.custom = 1
    dt.istable = 1
    dt.allow_rename = 1
    for fd in (
        {"fieldname": "ip_address", "label": "IP Address", "fieldtype": "Data"},
        {"fieldname": "device_name", "label": "Device Name", "fieldtype": "Data"},
        {"fieldname": "notes", "label": "Notes", "fieldtype": "Small Text"},
    ):
        dt.append('fields', fd)
    dt.insert(ignore_permissions=True)
    return 'created'


def _ensure_cf(dt, fieldname, fieldtype, options=None, insert_after=None, label=None):
    cf_name = f"{dt}-{fieldname}"
    if frappe.db.exists('Custom Field', cf_name):
        return 'exists'
    from frappe.custom.doctype.custom_field.custom_field import create_custom_field
    create_custom_field(dt, {
        'fieldname': fieldname,
        'label': label or fieldname.replace('_',' ').title(),
        'fieldtype': fieldtype,
        'options': options or '',
        'insert_after': insert_after or '',
    })
    return 'created'


def create_page():
    """Create Desk Page `sigma-desk` so page_js hook can attach.
    Avoids route conflicts with website route `sigma-dashboard`.
    """
    name = 'sigma-desk'
    if frappe.db.exists('Page', name):
        return {'status': 'exists'}
    page = frappe.new_doc('Page')
    page.page_name = name
    page.module = 'Sigma Home'
    page.title = 'Sigma Desk'
    page.insert(ignore_permissions=True)
    return {'status': 'created', 'page': page.name}


def create_customizations():
    """Create all custom fields and child DocTypes for ERPNext/Helpdesk integration."""
    results = {}
    # Child table
    results['Asset IP Address'] = _ensure_child_doctype_asset_ip()

    # ERPNext Asset CFs
    for args in [
        ('Asset','is_networked','Check',None,'item_code'),
        ('Asset','ip_address','Data',None,'item_code'),
        ('Asset','parent_asset','Link','Asset',None),
        ('Asset','is_tracking_device','Check',None,None),
        ('Asset','last_known_latitude','Float',None,None),
        ('Asset','last_known_longitude','Float',None,None),
        ('Asset','last_location_update','Datetime',None,None),
        ('Asset','ip_addresses','Table','Asset IP Address',None),
    ]:
        results[f"{args[0]}-{args[1]}"] = _ensure_cf(*args)

    # Sigma <-> ERPNext links
    results['Access Point-erpnext_asset'] = _ensure_cf('Access Point', 'erpnext_asset', 'Link', 'Asset')
    results['Access Event-erpnext_asset'] = _ensure_cf('Access Event', 'erpnext_asset', 'Link', 'Asset')

    # Helpdesk links
    results['Call Log-helpdesk_ticket'] = _ensure_cf('Call Log', 'helpdesk_ticket', 'Link', 'HD Ticket')
    results['Call Log-severity'] = _ensure_cf('Call Log', 'severity', 'Select', '\nLow\nMedium\nHigh\nCritical')
    results['Call Log-description'] = _ensure_cf('Call Log', 'description', 'Small Text')
    results['Call Log-caller_name'] = _ensure_cf('Call Log', 'caller_name', 'Data')
    # Safe attempts for cross-links with Case Record; skip if module import fails
    try:
        results['Call Log-linked_case'] = _ensure_cf('Call Log', 'linked_case', 'Link', 'Case Record')
    except Exception as e:
        results['Call Log-linked_case'] = f'skipped: {e}'
    try:
        results['Case Record-helpdesk_ticket'] = _ensure_cf('Case Record', 'helpdesk_ticket', 'Link', 'HD Ticket')
    except Exception as e:
        results['Case Record-helpdesk_ticket'] = f'skipped: {e}'
    try:
        results['HD Ticket-sigma_case'] = _ensure_cf('HD Ticket', 'sigma_case', 'Link', 'Case Record')
    except Exception as e:
        results['HD Ticket-sigma_case'] = f'skipped: {e}'
    results['HD Ticket-call_log'] = _ensure_cf('HD Ticket', 'call_log', 'Link', 'Call Log')

    frappe.db.commit()
    return results


def create_dashboard_charts():
    """Create KPI Number Cards and Trend Dashboard Charts for Sigma workspace."""
    created = {"number_cards": [], "dashboard_charts": []}

    def make_number_card(name, label, doctype, filters=None):
        if frappe.db.exists('Number Card', name):
            return 'exists'
        nc = frappe.new_doc('Number Card')
        nc.name = name
        nc.label = label
        nc.document_type = doctype
        nc.function = 'Count'
        nc.filters_json = json.dumps(filters or {})
        nc.is_public = 1
        nc.insert(ignore_permissions=True)
        created["number_cards"].append(name)
        return 'created'

    def make_chart(name, chart_name, doctype, vtype, filters=None, group_by=None):
        if frappe.db.exists('Dashboard Chart', name):
            return 'exists'
        chart = frappe.new_doc('Dashboard Chart')
        chart.name = name
        chart.chart_name = chart_name
        chart.document_type = doctype
        chart.chart_type = 'Count'
        chart.type = vtype
        chart.filters_json = json.dumps(filters or {})
        if group_by:
            chart.group_by_based_on = group_by
            chart.group_by_type = 'Count'
        if vtype == 'Line':
            chart.timeseries = 1
            chart.time_interval = 'Daily'
            chart.timespan = 'Last Week'
            chart.based_on = 'timestamp' if frappe.db.has_column(doctype, 'timestamp') else 'creation'
        else:
            chart.timeseries = 0
            chart.based_on = 'creation'
        chart.is_public = 1
        chart.insert(ignore_permissions=True)
        created["dashboard_charts"].append(name)
        return 'created'

    today = getdate(now_datetime())
    today_str = str(today)

    # KPI Number Cards
    make_number_card('Open Cases', 'Open Cases', 'Case Record', {"status": "Open"})
    make_number_card('Access Denied Today', 'Access Denied Today', 'Access Event', {"result": "Denied", "timestamp": [">=", today_str]})
    make_number_card('Active Guards', 'Active Guards', 'Guard Shift', {"status": "Active"})
    make_number_card('Access Events Today', 'Access Events Today', 'Access Event', {"timestamp": [">=", today_str]})

    # Trend / Distribution Charts
    make_chart('Access Events Trend', 'Access Events Trend', 'Access Event', 'Line')
    make_chart('Cases by Status', 'Cases by Status', 'Case Record', 'Donut', None, 'status')
    make_chart('Risk Assessment Distribution', 'Risk Assessment Distribution', 'Risk Assessment', 'Bar', None, 'risk_level')
    if frappe.db.exists('DocType', 'Guard Activity'):
        make_chart('Guard Activity Metrics', 'Guard Activity Metrics', 'Guard Activity', 'Line', None, 'activity_type')

    frappe.db.commit()
    return created

