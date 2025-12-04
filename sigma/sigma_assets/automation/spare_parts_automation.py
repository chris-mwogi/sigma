# Copyright (c) 2025, Augment and contributors
# For license information, please see license.txt

"""
Spare Parts Auto-Reorder System
"""

import frappe
from frappe.utils import nowdate, add_days, flt, cint
from datetime import datetime


def calculate_reorder_point(item_code):
    """
    Calculate reorder point based on:
    - Average consumption rate
    - Lead time
    - Safety stock

    Reorder Point = (Average Daily Usage × Lead Time) + Safety Stock
    """
    # Get consumption history (last 90 days)
    consumption = frappe.db.sql("""
        SELECT
            SUM(qty) as total_qty,
            COUNT(DISTINCT DATE(posting_date)) as days_count
        FROM
            `tabStock Entry Detail`
        WHERE
            item_code = %(item_code)s
            AND s_warehouse IS NOT NULL
            AND posting_date >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
    """, {"item_code": item_code}, as_dict=1)

    if not consumption or not consumption[0].total_qty:
        # No consumption history, use default reorder level of 10
        return 10.0

    # Calculate average daily usage
    total_qty = flt(consumption[0].total_qty)
    days_count = cint(consumption[0].days_count) or 1
    avg_daily_usage = total_qty / days_count

    # Get lead time (default 7 days if not specified)
    lead_time_days = 7.0

    # Calculate safety stock (20% of lead time demand)
    safety_stock = avg_daily_usage * lead_time_days * 0.20

    # Calculate reorder point
    reorder_point = (avg_daily_usage * lead_time_days) + safety_stock

    return round(reorder_point, 2)


def check_spare_parts_inventory():
    """
    Check spare parts inventory levels and create purchase requests
    Runs daily
    """
    frappe.logger().info("Starting spare parts inventory check...")
    
    # Get all spare parts items (items linked to assets)
    spare_parts = frappe.db.sql("""
        SELECT DISTINCT
            i.item_code,
            i.item_name,
            SUM(bin.actual_qty) as current_stock,
            SUM(bin.ordered_qty) as ordered_qty,
            SUM(bin.reserved_qty) as reserved_qty
        FROM
            `tabItem` i
        LEFT JOIN
            `tabBin` bin ON i.item_code = bin.item_code
        WHERE
            i.sigma_asset IS NOT NULL
            AND i.disabled = 0
            AND i.is_stock_item = 1
        GROUP BY
            i.item_code
        HAVING
            current_stock IS NOT NULL
    """, as_dict=1)
    
    requests_created = 0
    
    for item in spare_parts:
        try:
            # Calculate dynamic reorder point
            reorder_point = calculate_reorder_point(item.item_code)
            
            # Calculate available stock (current - reserved)
            available_stock = flt(item.current_stock) - flt(item.reserved_qty)
            
            # Check if reorder is needed
            if available_stock <= reorder_point and flt(item.ordered_qty) == 0:
                # Check if purchase request already exists
                existing_pr = frappe.db.exists("Material Request Item", {
                    "item_code": item.item_code,
                    "parent": ["in", frappe.db.get_all("Material Request", {
                        "docstatus": ["<", 2],
                        "status": ["not in", ["Stopped", "Cancelled"]],
                        "material_request_type": "Purchase"
                    }, pluck="name")]
                })
                
                if not existing_pr:
                    # Calculate order quantity (default 10 units)
                    reorder_qty = 10.0
                    shortage = reorder_point - available_stock
                    order_qty = max(reorder_qty, shortage)
                    
                    # Create Material Request
                    mr = frappe.get_doc({
                        "doctype": "Material Request",
                        "material_request_type": "Purchase",
                        "transaction_date": nowdate(),
                        "schedule_date": add_days(nowdate(), 7),
                        "company": frappe.defaults.get_user_default("Company"),
                        "items": [{
                            "item_code": item.item_code,
                            "qty": order_qty,
                            "schedule_date": add_days(nowdate(), 7),
                            "warehouse": frappe.db.get_value("Item", item.item_code, "default_warehouse")
                        }]
                    })

                    # Note: default_supplier field doesn't exist in Item DocType
                    # Supplier would need to be set manually or from Item Reorder table

                    mr.insert(ignore_permissions=True)
                    mr.submit()
                    
                    requests_created += 1
                    
                    frappe.logger().info(
                        f"Created purchase request for {item.item_code}: "
                        f"Available: {available_stock}, Reorder Point: {reorder_point}, Qty: {order_qty}"
                    )
        
        except Exception as e:
            frappe.logger().error(f"Error creating purchase request for {item.item_code}: {str(e)}")
            continue
    
    frappe.db.commit()
    frappe.logger().info(f"Created {requests_created} spare parts purchase requests")
    
    return requests_created

