import frappe

@frappe.whitelist()
def get_risk_summary():
    """Return risk summary by level and category, optionally filtered by assessment_type"""
    assessment_type = frappe.form_dict.get('assessment_type')

    filters = ""
    if assessment_type:
        filters = frappe.db.escape(assessment_type)
        filters = f"WHERE assessment_type = '{filters}'"

    by_level = frappe.db.sql(f"""
        SELECT risk_level, COUNT(*) AS count
        FROM `tabRisk Assessment`
        {filters}
        GROUP BY risk_level
    """, as_dict=True)

    by_category = frappe.db.sql(f"""
        SELECT risk_category, COUNT(*) AS count
        FROM `tabRisk Assessment`
        {filters}
        GROUP BY risk_category
    """, as_dict=True)

    top_open = frappe.db.sql("""
        SELECT name, assessment_title, risk_level, risk_score, assessment_type, responsible_department, linked_location
        FROM `tabRisk Assessment`
        WHERE status IN ('Open','In Progress')
        ORDER BY risk_score DESC
        LIMIT 10
    """, as_dict=True)

    return {"by_level": by_level, "by_category": by_category, "top_open": top_open}
