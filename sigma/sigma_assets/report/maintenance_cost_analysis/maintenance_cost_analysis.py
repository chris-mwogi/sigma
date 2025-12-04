# Copyright (c) 2025, Augment and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate, add_months


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data, filters)
    summary = get_summary(data)
    
    return columns, data, None, chart, summary


def get_columns():
    return [
        {
            "fieldname": "asset",
            "label": _("Asset"),
            "fieldtype": "Link",
            "options": "Asset",
            "width": 180
        },
        {
            "fieldname": "asset_name",
            "label": _("Asset Name"),
            "fieldtype": "Data",
            "width": 180
        },
        {
            "fieldname": "asset_category_sigma",
            "label": _("Category"),
            "fieldtype": "Link",
            "options": "Asset Category Sigma",
            "width": 150
        },
        {
            "fieldname": "preventive_cost",
            "label": _("Preventive Cost"),
            "fieldtype": "Currency",
            "width": 140
        },
        {
            "fieldname": "corrective_cost",
            "label": _("Corrective Cost"),
            "fieldtype": "Currency",
            "width": 140
        },
        {
            "fieldname": "predictive_cost",
            "label": _("Predictive Cost"),
            "fieldtype": "Currency",
            "width": 140
        },
        {
            "fieldname": "total_cost",
            "label": _("Total Cost"),
            "fieldtype": "Currency",
            "width": 140
        },
        {
            "fieldname": "work_order_count",
            "label": _("Work Orders"),
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "avg_cost_per_wo",
            "label": _("Avg Cost/WO"),
            "fieldtype": "Currency",
            "width": 130
        },
        {
            "fieldname": "cost_trend",
            "label": _("Cost Trend"),
            "fieldtype": "Data",
            "width": 120
        }
    ]


def get_data(filters):
    conditions = get_conditions(filters)
    
    # Get maintenance costs by asset and type
    data = frappe.db.sql(f"""
        SELECT 
            wo.asset,
            a.asset_name,
            a.asset_category_sigma,
            SUM(CASE WHEN wo.work_order_type = 'Preventive Maintenance' 
                THEN COALESCE(wo.actual_cost, wo.estimated_cost, 0) 
                ELSE 0 END) as preventive_cost,
            SUM(CASE WHEN wo.work_order_type = 'Corrective Maintenance' 
                THEN COALESCE(wo.actual_cost, wo.estimated_cost, 0) 
                ELSE 0 END) as corrective_cost,
            SUM(CASE WHEN wo.work_order_type = 'Predictive Maintenance' 
                THEN COALESCE(wo.actual_cost, wo.estimated_cost, 0) 
                ELSE 0 END) as predictive_cost,
            SUM(COALESCE(wo.actual_cost, wo.estimated_cost, 0)) as total_cost,
            COUNT(wo.name) as work_order_count
        FROM 
            `tabAsset Work Order` wo
        INNER JOIN 
            `tabAsset` a ON a.name = wo.asset
        WHERE 
            wo.docstatus = 1
            {conditions}
        GROUP BY 
            wo.asset
        ORDER BY 
            total_cost DESC
    """, as_dict=1)
    
    # Calculate average cost per work order and cost trend
    for row in data:
        row.avg_cost_per_wo = flt(row.total_cost) / flt(row.work_order_count) if row.work_order_count > 0 else 0
        
        # Determine cost trend (simplified - comparing preventive vs corrective)
        if flt(row.corrective_cost) > flt(row.preventive_cost) * 1.5:
            row.cost_trend = "High Reactive"
        elif flt(row.preventive_cost) > flt(row.corrective_cost):
            row.cost_trend = "Proactive"
        else:
            row.cost_trend = "Balanced"
    
    return data


def get_conditions(filters):
    conditions = []
    
    if filters.get("asset"):
        conditions.append(f"AND wo.asset = '{filters.get('asset')}'")
    
    if filters.get("asset_category_sigma"):
        conditions.append(f"AND a.asset_category_sigma = '{filters.get('asset_category_sigma')}'")
    
    if filters.get("asset_location"):
        conditions.append(f"AND a.asset_location = '{filters.get('asset_location')}'")
    
    if filters.get("from_date"):
        conditions.append(f"AND wo.scheduled_start_date >= '{filters.get('from_date')}'")
    
    if filters.get("to_date"):
        conditions.append(f"AND wo.scheduled_end_date <= '{filters.get('to_date')}'")
    
    if filters.get("work_order_type"):
        conditions.append(f"AND wo.work_order_type = '{filters.get('work_order_type')}'")
    
    return " ".join(conditions)


def get_chart_data(data, filters):
    if not data:
        return None
    
    # Cost breakdown by maintenance type
    total_preventive = sum([flt(row.get("preventive_cost", 0)) for row in data])
    total_corrective = sum([flt(row.get("corrective_cost", 0)) for row in data])
    total_predictive = sum([flt(row.get("predictive_cost", 0)) for row in data])
    
    return {
        "data": {
            "labels": ["Preventive", "Corrective", "Predictive"],
            "datasets": [
                {
                    "name": "Maintenance Cost",
                    "values": [
                        round(total_preventive, 2),
                        round(total_corrective, 2),
                        round(total_predictive, 2)
                    ]
                }
            ]
        },
        "type": "pie",
        "colors": ["#28a745", "#dc3545", "#17a2b8"]
    }


def get_summary(data):
    if not data:
        return []
    
    total_assets = len(data)
    total_cost = sum([flt(row.get("total_cost", 0)) for row in data])
    total_preventive = sum([flt(row.get("preventive_cost", 0)) for row in data])
    total_corrective = sum([flt(row.get("corrective_cost", 0)) for row in data])
    total_work_orders = sum([row.get("work_order_count", 0) for row in data])
    avg_cost_per_asset = total_cost / total_assets if total_assets > 0 else 0
    
    # Calculate preventive vs corrective ratio
    preventive_ratio = (total_preventive / total_cost * 100) if total_cost > 0 else 0
    
    return [
        {
            "value": total_assets,
            "indicator": "blue",
            "label": "Assets with Maintenance",
            "datatype": "Int"
        },
        {
            "value": round(total_cost, 2),
            "indicator": "orange",
            "label": "Total Maintenance Cost",
            "datatype": "Currency"
        },
        {
            "value": round(avg_cost_per_asset, 2),
            "indicator": "blue",
            "label": "Avg Cost per Asset",
            "datatype": "Currency"
        },
        {
            "value": total_work_orders,
            "indicator": "blue",
            "label": "Total Work Orders",
            "datatype": "Int"
        },
        {
            "value": round(preventive_ratio, 2),
            "indicator": "green" if preventive_ratio >= 60 else "red",
            "label": "Preventive Maintenance %",
            "datatype": "Percent"
        }
    ]

