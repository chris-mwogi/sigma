from . import __version__ as app_version

app_name = "sigma"
app_title = "Sigma"
app_publisher = "Prismod Technologies Limited"
app_description = "Case Management for Power Utility Security Department"
app_icon = "octicon octicon-shield"
app_color = "blue"
app_email = "support@prismod.co.ke"
app_license = "MIT"

# Include module pages
app_include_js = "/assets/sigma/js/case_utils.js"

# Fixtures (optional)
fixtures = [
    {"doctype": "Workflow", "filters": [["name", "in", ["Case Workflow"]]]},
    {"doctype": "Role", "filters": [["name", "in", ["Security Officer", "Legal Officer", "Case Supervisor"]]]},
    {"doctype": "Custom Field", "filters": [["dt", "=", "Case"]]},
    {"doctype": "Property Setter", "filters": [["doc_type", "in", ["Asset", "Issue"]]]}
]

# Portal Menu
website_context = {
    "top_bar_items": [
        {"label": "Cases", "url": "/cases", "role": "Customer"}
    ]
}

# Allow guest access
website_generators = ["Case"]  # Automatically generate pages for each Case

# Expose API methods for portal/integration
override_whitelisted_methods = {
    "sigma.sigma_case_management.api.cases_api.get_cases": "sigma.sigma_case_management.api.cases_api.get_cases",
}
