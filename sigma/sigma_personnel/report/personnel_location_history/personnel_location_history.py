# Copyright (c) 2025, Prismod Technologies Limited and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, add_days


def execute(filters=None):
    """
    Personnel Location History Report
    Tracks personnel movement history across zones and locations
    """
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)
    return columns, data, None, chart


def get_columns():
    """Define report columns"""
    return [
        {
            "fieldname": "event_id",
            "label": _("Event ID"),
            "fieldtype": "Link",
            "options": "Human Location Event",
            "width": 120
        },
        {
            "fieldname": "human",
            "label": _("Personnel"),
            "fieldtype": "Link",
            "options": "Human Profile",
            "width": 120
        },
        {
            "fieldname": "human_name",
            "label": _("Name"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "source_type",
            "label": _("Source Type"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "zone",
            "label": _("Zone"),
            "fieldtype": "Link",
            "options": "Zone Configuration",
            "width": 120
        },
        {
            "fieldname": "zone_name",
            "label": _("Zone Name"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "timestamp",
            "label": _("Timestamp"),
            "fieldtype": "Datetime",
            "width": 150
        },
        {
            "fieldname": "source_id",
            "label": _("Source ID"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "confidence",
            "label": _("Confidence (%)"),
            "fieldtype": "Percent",
            "width": 100
        },
        {
            "fieldname": "latitude",
            "label": _("Latitude"),
            "fieldtype": "Float",
            "precision": 6,
            "width": 100
        },
        {
            "fieldname": "longitude",
            "label": _("Longitude"),
            "fieldtype": "Float",
            "precision": 6,
            "width": 100
        }
    ]


def get_data(filters):
    """Get personnel location history data"""
    conditions = {}

    if filters:
        if filters.get("from_date"):
            conditions["timestamp"] = [">=", filters.get("from_date")]
        if filters.get("to_date"):
            conditions["timestamp"] = ["<=", add_days(filters.get("to_date"), 1)]
        if filters.get("human"):
            conditions["human"] = filters.get("human")
        if filters.get("source_type"):
            conditions["source_type"] = filters.get("source_type")

    events = frappe.get_all("Human Location Event",
        filters=conditions,
        fields=["name", "human", "source_type", "zone", "timestamp",
                "source_id", "confidence", "latitude", "longitude"],
        order_by="timestamp desc",
        limit=1000
    )

    data = []
    for event in events:
        # Get human name
        human_name = frappe.db.get_value("Human Profile", event.human, "full_name") or ""

        # Get zone name
        zone_name = ""
        if event.zone:
            zone_name = frappe.db.get_value("Zone Configuration", event.zone, "zone_name") or ""

        data.append({
            "event_id": event.name,
            "human": event.human,
            "human_name": human_name,
            "source_type": event.source_type,
            "zone": event.zone,
            "zone_name": zone_name,
            "timestamp": event.timestamp,
            "source_id": event.source_id,
            "confidence": event.confidence,
            "latitude": event.latitude,
            "longitude": event.longitude
        })

    return data


def get_chart_data(data):
    """Generate chart showing events by source type"""
    type_counts = {}
    for d in data:
        stype = d.get("source_type") or "Unknown"
        type_counts[stype] = type_counts.get(stype, 0) + 1

    return {
        "data": {
            "labels": list(type_counts.keys()),
            "datasets": [{"name": "Events", "values": list(type_counts.values())}]
        },
        "type": "bar",
        "colors": ["#4CAF50", "#2196F3", "#FF9800", "#9C27B0"]
    }

