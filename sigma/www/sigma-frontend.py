import frappe

def get_context(context):
    """
    Context for Sigma Frontend page
    """
    context.no_cache = 1
    context.show_sidebar = False

    # Set page title and meta
    context.title = "Sigma"
    context.page_title = "Sigma - Security Management System"

    return context

