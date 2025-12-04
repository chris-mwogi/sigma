# Copyright (c) 2025, Augment and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate, date_diff, nowdate


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)
    summary = get_summary(data)
    
    return columns, data, None, chart, summary


def get_columns():
    return [
        {
            "fieldname": "asset",
            "label": _("Asset"),
            "fieldtype": "Link",
            "options": "Asset",
            "width": 200
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
            "fieldname": "asset_location",
            "label": _("Location"),
            "fieldtype": "Link",
            "options": "Asset Location",
            "width": 150
        },
        {
            "fieldname": "lifecycle_status",
            "label": _("Status"),
            "fieldtype": "Select",
            "width": 120
        },
        {
            "fieldname": "total_uptime_hours",
            "label": _("Uptime (Hours)"),
            "fieldtype": "Float",
            "width": 120
        },
        {
            "fieldname": "total_downtime_hours",
            "label": _("Downtime (Hours)"),
            "fieldtype": "Float",
            "width": 120
        },
        {
            "fieldname": "utilization_rate",
            "label": _("Utilization %"),
            "fieldtype": "Percent",
            "width": 120
        },
        {
            "fieldname": "availability_rate",
            "label": _("Availability %"),
            "fieldtype": "Percent",
            "width": 120
        },
        {
            "fieldname": "maintenance_hours",
            "label": _("Maintenance (Hours)"),
            "fieldtype": "Float",
            "width": 140
        },
        {
            "fieldname": "idle_hours",
            "label": _("Idle (Hours)"),
            "fieldtype": "Float",
            "width": 120
        },
        {
            "fieldname": "utilization_status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 120
        }
    ]


def get_data(filters):
    conditions = get_conditions(filters)
    
    # Get assets with work order statistics
    data = frappe.db.sql(f"""
        SELECT 
            a.name as asset,
            a.asset_name,
            a.asset_category_sigma,
            a.asset_location,
            a.lifecycle_status,
            a.commissioning_date,
            COALESCE(SUM(CASE WHEN wo.work_order_status = 'Completed' 
                THEN TIMESTAMPDIFF(HOUR, wo.actual_start_date, wo.actual_end_date) 
                ELSE 0 END), 0) as maintenance_hours,
            COUNT(DISTINCT wo.name) as total_work_orders,
            COALESCE(SUM(CASE WHEN wo.work_order_status IN ('In Progress', 'On Hold') 
                THEN TIMESTAMPDIFF(HOUR, wo.actual_start_date, NOW()) 
                ELSE 0 END), 0) as current_downtime_hours
        FROM 
            `tabAsset` a
        LEFT JOIN 
            `tabAsset Work Order` wo ON wo.asset = a.name AND wo.docstatus = 1
        WHERE 
            a.docstatus = 1
            {conditions}
        GROUP BY 
            a.name
        ORDER BY 
            a.asset_name
    """, as_dict=1)
    
    # Calculate utilization metrics
    for row in data:
        # Calculate total operational time since commissioning
        if row.commissioning_date:
            days_operational = date_diff(nowdate(), row.commissioning_date)
            total_hours = days_operational * 24
        else:
            total_hours = 0
        
        # Calculate downtime (maintenance + current downtime)
        total_downtime = flt(row.maintenance_hours) + flt(row.current_downtime_hours)
        
        # Calculate uptime
        total_uptime = max(0, total_hours - total_downtime)
        
        # Calculate utilization rate (uptime / total time)
        utilization_rate = (total_uptime / total_hours * 100) if total_hours > 0 else 0
        
        # Calculate availability rate (1 - downtime/total time)
        availability_rate = ((total_hours - total_downtime) / total_hours * 100) if total_hours > 0 else 0
        
        # Calculate idle hours (uptime - productive time, assuming 80% productive)
        productive_hours = total_uptime * 0.8
        idle_hours = total_uptime - productive_hours
        
        # Determine utilization status
        if utilization_rate >= 80:
            utilization_status = "Excellent"
        elif utilization_rate >= 60:
            utilization_status = "Good"
        elif utilization_rate >= 40:
            utilization_status = "Fair"
        else:
            utilization_status = "Poor"
        
        row.update({
            "total_uptime_hours": round(total_uptime, 2),
            "total_downtime_hours": round(total_downtime, 2),
            "utilization_rate": round(utilization_rate, 2),
            "availability_rate": round(availability_rate, 2),
            "idle_hours": round(idle_hours, 2),
            "utilization_status": utilization_status
        })
    
    return data


def get_conditions(filters):
    conditions = []
    
    if filters.get("asset"):
        conditions.append(f"AND a.name = '{filters.get('asset')}'")
    
    if filters.get("asset_category_sigma"):
        conditions.append(f"AND a.asset_category_sigma = '{filters.get('asset_category_sigma')}'")
    
    if filters.get("asset_location"):
        conditions.append(f"AND a.asset_location = '{filters.get('asset_location')}'")
    
    if filters.get("lifecycle_status"):
        conditions.append(f"AND a.lifecycle_status = '{filters.get('lifecycle_status')}'")
    
    if filters.get("criticality_rating"):
        conditions.append(f"AND a.criticality_rating = '{filters.get('criticality_rating')}'")
    
    return " ".join(conditions)


def get_chart_data(data):
    if not data:
        return None
    
    # Utilization status distribution
    status_counts = {}
    for row in data:
        status = row.get("utilization_status", "Unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
    
    return {
        "data": {
            "labels": list(status_counts.keys()),
            "datasets": [
                {
                    "name": "Asset Count",
                    "values": list(status_counts.values())
                }
            ]
        },
        "type": "donut",
        "colors": ["#28a745", "#17a2b8", "#ffc107", "#dc3545"]
    }


def get_summary(data):
    if not data:
        return []
    
    total_assets = len(data)
    avg_utilization = sum([row.get("utilization_rate", 0) for row in data]) / total_assets if total_assets > 0 else 0
    avg_availability = sum([row.get("availability_rate", 0) for row in data]) / total_assets if total_assets > 0 else 0
    total_downtime = sum([row.get("total_downtime_hours", 0) for row in data])
    excellent_assets = len([row for row in data if row.get("utilization_status") == "Excellent"])
    
    return [
        {
            "value": total_assets,
            "indicator": "blue",
            "label": "Total Assets",
            "datatype": "Int"
        },
        {
            "value": round(avg_utilization, 2),
            "indicator": "green" if avg_utilization >= 70 else "orange",
            "label": "Avg Utilization %",
            "datatype": "Percent"
        },
        {
            "value": round(avg_availability, 2),
            "indicator": "green" if avg_availability >= 90 else "orange",
            "label": "Avg Availability %",
            "datatype": "Percent"
        },
        {
            "value": round(total_downtime, 2),
            "indicator": "red",
            "label": "Total Downtime (Hours)",
            "datatype": "Float"
        },
        {
            "value": excellent_assets,
            "indicator": "green",
            "label": "Excellent Utilization",
            "datatype": "Int"
        }
    ]

