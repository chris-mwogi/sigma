# Copyright (c) 2025, Augment and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate, date_diff, time_diff_in_hours


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
            "fieldname": "criticality_rating",
            "label": _("Criticality"),
            "fieldtype": "Select",
            "width": 120
        },
        {
            "fieldname": "total_downtime_hours",
            "label": _("Total Downtime (Hours)"),
            "fieldtype": "Float",
            "width": 160
        },
        {
            "fieldname": "planned_downtime_hours",
            "label": _("Planned (Hours)"),
            "fieldtype": "Float",
            "width": 140
        },
        {
            "fieldname": "unplanned_downtime_hours",
            "label": _("Unplanned (Hours)"),
            "fieldtype": "Float",
            "width": 150
        },
        {
            "fieldname": "downtime_incidents",
            "label": _("Incidents"),
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "mttr_hours",
            "label": _("MTTR (Hours)"),
            "fieldtype": "Float",
            "width": 120
        },
        {
            "fieldname": "availability_percentage",
            "label": _("Availability %"),
            "fieldtype": "Percent",
            "width": 130
        },
        {
            "fieldname": "downtime_status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 120
        }
    ]


def get_data(filters):
    conditions = get_conditions(filters)
    
    # Get downtime data from work orders
    data = frappe.db.sql(f"""
        SELECT 
            a.name as asset,
            a.asset_name,
            a.asset_category_sigma,
            a.criticality_rating,
            a.commissioning_date,
            COUNT(wo.name) as downtime_incidents,
            SUM(CASE 
                WHEN wo.actual_start_date IS NOT NULL AND wo.actual_end_date IS NOT NULL 
                THEN TIMESTAMPDIFF(HOUR, wo.actual_start_date, wo.actual_end_date)
                WHEN wo.actual_start_date IS NOT NULL AND wo.work_order_status IN ('In Progress', 'On Hold')
                THEN TIMESTAMPDIFF(HOUR, wo.actual_start_date, NOW())
                ELSE COALESCE(wo.estimated_duration_hours, 0)
            END) as total_downtime_hours,
            SUM(CASE 
                WHEN wo.work_order_type IN ('Preventive Maintenance', 'Predictive Maintenance')
                THEN CASE 
                    WHEN wo.actual_start_date IS NOT NULL AND wo.actual_end_date IS NOT NULL 
                    THEN TIMESTAMPDIFF(HOUR, wo.actual_start_date, wo.actual_end_date)
                    ELSE COALESCE(wo.estimated_duration_hours, 0)
                END
                ELSE 0
            END) as planned_downtime_hours,
            SUM(CASE 
                WHEN wo.work_order_type IN ('Corrective Maintenance', 'Emergency Maintenance')
                THEN CASE 
                    WHEN wo.actual_start_date IS NOT NULL AND wo.actual_end_date IS NOT NULL 
                    THEN TIMESTAMPDIFF(HOUR, wo.actual_start_date, wo.actual_end_date)
                    ELSE COALESCE(wo.estimated_duration_hours, 0)
                END
                ELSE 0
            END) as unplanned_downtime_hours
        FROM 
            `tabAsset` a
        LEFT JOIN 
            `tabAsset Work Order` wo ON wo.asset = a.name AND wo.docstatus = 1
        WHERE 
            a.docstatus = 1
            {conditions}
        GROUP BY 
            a.name
        HAVING 
            total_downtime_hours > 0
        ORDER BY 
            total_downtime_hours DESC
    """, as_dict=1)
    
    # Calculate MTTR and availability
    for row in data:
        # Mean Time To Repair (MTTR)
        row.mttr_hours = flt(row.total_downtime_hours) / flt(row.downtime_incidents) if row.downtime_incidents > 0 else 0
        
        # Calculate availability percentage
        if row.commissioning_date:
            days_operational = date_diff(getdate(), row.commissioning_date)
            total_hours = days_operational * 24
            uptime_hours = total_hours - flt(row.total_downtime_hours)
            row.availability_percentage = (uptime_hours / total_hours * 100) if total_hours > 0 else 0
        else:
            row.availability_percentage = 0
        
        # Determine downtime status
        if row.availability_percentage >= 99:
            row.downtime_status = "Excellent"
        elif row.availability_percentage >= 95:
            row.downtime_status = "Good"
        elif row.availability_percentage >= 90:
            row.downtime_status = "Fair"
        else:
            row.downtime_status = "Poor"
        
        # Round values
        row.total_downtime_hours = round(flt(row.total_downtime_hours), 2)
        row.planned_downtime_hours = round(flt(row.planned_downtime_hours), 2)
        row.unplanned_downtime_hours = round(flt(row.unplanned_downtime_hours), 2)
        row.mttr_hours = round(row.mttr_hours, 2)
        row.availability_percentage = round(row.availability_percentage, 2)
    
    return data


def get_conditions(filters):
    conditions = []
    
    if filters.get("asset"):
        conditions.append(f"AND a.name = '{filters.get('asset')}'")
    
    if filters.get("asset_category_sigma"):
        conditions.append(f"AND a.asset_category_sigma = '{filters.get('asset_category_sigma')}'")
    
    if filters.get("asset_location"):
        conditions.append(f"AND a.asset_location = '{filters.get('asset_location')}'")
    
    if filters.get("criticality_rating"):
        conditions.append(f"AND a.criticality_rating = '{filters.get('criticality_rating')}'")
    
    if filters.get("from_date"):
        conditions.append(f"AND wo.scheduled_start_date >= '{filters.get('from_date')}'")
    
    if filters.get("to_date"):
        conditions.append(f"AND wo.scheduled_end_date <= '{filters.get('to_date')}'")
    
    return " ".join(conditions)


def get_chart_data(data):
    if not data:
        return None
    
    # Top 10 assets by downtime
    top_assets = sorted(data, key=lambda x: x.get("total_downtime_hours", 0), reverse=True)[:10]
    
    return {
        "data": {
            "labels": [row.get("asset_name", "")[:20] for row in top_assets],
            "datasets": [
                {
                    "name": "Planned Downtime",
                    "values": [round(flt(row.get("planned_downtime_hours", 0)), 2) for row in top_assets]
                },
                {
                    "name": "Unplanned Downtime",
                    "values": [round(flt(row.get("unplanned_downtime_hours", 0)), 2) for row in top_assets]
                }
            ]
        },
        "type": "bar",
        "colors": ["#ffc107", "#dc3545"]
    }


def get_summary(data):
    if not data:
        return []
    
    total_assets = len(data)
    total_downtime = sum([flt(row.get("total_downtime_hours", 0)) for row in data])
    total_planned = sum([flt(row.get("planned_downtime_hours", 0)) for row in data])
    total_unplanned = sum([flt(row.get("unplanned_downtime_hours", 0)) for row in data])
    avg_availability = sum([row.get("availability_percentage", 0) for row in data]) / total_assets if total_assets > 0 else 0
    poor_availability = len([row for row in data if row.get("downtime_status") == "Poor"])
    
    return [
        {
            "value": total_assets,
            "indicator": "blue",
            "label": "Assets with Downtime",
            "datatype": "Int"
        },
        {
            "value": round(total_downtime, 2),
            "indicator": "red",
            "label": "Total Downtime (Hours)",
            "datatype": "Float"
        },
        {
            "value": round(total_unplanned, 2),
            "indicator": "red",
            "label": "Unplanned Downtime (Hours)",
            "datatype": "Float"
        },
        {
            "value": round(avg_availability, 2),
            "indicator": "green" if avg_availability >= 95 else "orange",
            "label": "Avg Availability %",
            "datatype": "Percent"
        },
        {
            "value": poor_availability,
            "indicator": "red" if poor_availability > 0 else "green",
            "label": "Poor Availability Assets",
            "datatype": "Int"
        }
    ]

