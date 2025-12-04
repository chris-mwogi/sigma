# Copyright (c) 2025, Augment and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    """Execute Compliance Status Report"""
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)
    summary = get_summary(data)
    
    return columns, data, None, chart, summary


def get_columns():
    """Define report columns"""
    return [
        {"fieldname": "asset", "label": _("Asset"), "fieldtype": "Link", "options": "Asset", "width": 150},
        {"fieldname": "asset_name", "label": _("Asset Name"), "fieldtype": "Data", "width": 180},
        {"fieldname": "asset_category_sigma", "label": _("Category"), "fieldtype": "Link", "options": "Asset Category Sigma", "width": 150},
        {"fieldname": "iso_55000_compliant", "label": _("ISO 55000"), "fieldtype": "Check", "width": 110},
        {"fieldname": "iso_14224_failure_code", "label": _("ISO 14224 Code"), "fieldtype": "Data", "width": 130},
        {"fieldname": "nist_compliant", "label": _("NIST"), "fieldtype": "Check", "width": 100},
        {"fieldname": "iec_61850_compliant", "label": _("IEC 61850"), "fieldtype": "Check", "width": 110},
        {"fieldname": "regulatory_compliance_status", "label": _("Regulatory Status"), "fieldtype": "Data", "width": 140},
        {"fieldname": "last_audit_date", "label": _("Last Audit"), "fieldtype": "Date", "width": 110}
    ]


def get_data(filters):
    """Get report data"""
    conditions = []
    if filters.get("asset_category_sigma"):
        conditions.append("AND a.asset_category_sigma = %(asset_category_sigma)s")
    
    conditions_str = " ".join(conditions)
    
    data = frappe.db.sql(f"""
        SELECT
            a.name as asset,
            a.asset_name,
            a.asset_category_sigma,
            a.iso_55000_compliant,
            a.iso_14224_failure_code,
            a.nist_compliant,
            a.iec_61850_compliant,
            a.regulatory_compliance_status,
            a.last_audit_date
        FROM
            `tabAsset` a
        WHERE
            a.docstatus = 1
            {conditions_str}
        ORDER BY
            a.last_audit_date DESC
    """, filters, as_dict=1)
    
    return data


def get_chart_data(data):
    """Generate chart data"""
    iso_55000_counts = {"Compliant": 0, "Partial": 0, "Non-Compliant": 0}
    for row in data:
        status = row.get("iso_55000_compliance", "Non-Compliant")
        if status in iso_55000_counts:
            iso_55000_counts[status] += 1
    
    return {
        "data": {
            "labels": list(iso_55000_counts.keys()),
            "datasets": [{"name": "ISO 55000 Compliance", "values": list(iso_55000_counts.values())}]
        },
        "type": "donut",
        "colors": ["#28a745", "#ffc107", "#dc3545"]
    }


def get_summary(data):
    """Generate summary statistics"""
    total = len(data)
    iso_compliant = len([d for d in data if d.get("iso_55000_compliance") == "Compliant"])
    nist_compliant = len([d for d in data if d.get("nist_compliance") == "Compliant"])
    regulatory_compliant = len([d for d in data if d.get("regulatory_compliance") == "Compliant"])
    
    return [
        {"value": total, "label": "Total Assets", "datatype": "Int", "indicator": "blue"},
        {"value": iso_compliant, "label": "ISO 55000 Compliant", "datatype": "Int", "indicator": "green"},
        {"value": nist_compliant, "label": "NIST Compliant", "datatype": "Int", "indicator": "green"},
        {"value": regulatory_compliant, "label": "Regulatory Compliant", "datatype": "Int", "indicator": "green"}
    ]

