import frappe
from frappe import _

@frappe.whitelist(allow_guest=False)
def get_cases():
    """
    GET /api/method/sigma.sigma_case_management.api.cases_api.get_cases
    Returns all cases for the logged-in user
    """
    return frappe.get_all("Case",
                          filters={"owner": frappe.session.user},
                          fields=["name", "case_type", "status", "description"])

@frappe.whitelist(allow_guest=False)
def get_case(case_name):
    """
    GET /api/method/sigma.sigma_case_management.api.cases_api.get_case?case_name=CAS-0001
    Return a single case by name
    """
    return frappe.get_doc("Case", case_name)

@frappe.whitelist(allow_guest=False)
def create_case(case_type, description, asset=None):
    """
    POST /api/method/sigma.sigma_case_management.api.cases_api.create_case
    Creates a new Case
    """
    doc = frappe.get_doc({
        "doctype": "Case",
        "case_type": case_type,
        "description": description,
        "asset_link": asset
    })
    doc.insert()
    return doc

@frappe.whitelist(allow_guest=False)
def update_case(case_name, status=None, description=None):
    """
    PUT /api/method/sigma.sigma_case_management.api.cases_api.update_case
    Updates an existing Case
    """
    doc = frappe.get_doc("Case", case_name)
    if status:
        doc.status = status
    if description:
        doc.description = description
    doc.save()
    return doc

@frappe.whitelist(allow_guest=False)
def delete_case(case_name):
    """
    DELETE /api/method/sigma.sigma_case_management.api.cases_api.delete_case
    Deletes a Case
    """
    frappe.delete_doc("Case", case_name)
    return {"message": _("Case deleted")}
