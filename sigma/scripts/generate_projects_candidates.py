import frappe
import json
import os
from difflib import SequenceMatcher


def similarity_score(a, b):
    """Calculate similarity score between two strings (0 to 1)."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def find_candidates_for_name(unresolved_name, top_n=5):
    """
    Find top N candidates (DocType/Report/Dashboard/Page) for an unresolved name.
    Returns list of dicts: [{'type': 'DocType', 'name': 'xyz', 'score': 0.95}, ...]
    """
    candidates = []
    
    # Search in DocTypes
    doctypes = frappe.db.sql("SELECT name FROM `tabDocType` LIMIT 1000", as_list=True)
    for (dt_name,) in doctypes:
        score = similarity_score(unresolved_name, dt_name)
        if score > 0.5:  # threshold
            candidates.append({'type': 'DocType', 'name': dt_name, 'score': round(score, 3)})
    
    # Search in Reports
    reports = frappe.db.sql("SELECT name FROM `tabReport` LIMIT 500", as_list=True)
    for (report_name,) in reports:
        score = similarity_score(unresolved_name, report_name)
        if score > 0.5:
            candidates.append({'type': 'Report', 'name': report_name, 'score': round(score, 3)})
    
    # Search in Dashboards
    dashboards = frappe.db.sql("SELECT name FROM `tabDashboard` LIMIT 500", as_list=True)
    for (dashboard_name,) in dashboards:
        score = similarity_score(unresolved_name, dashboard_name)
        if score > 0.5:
            candidates.append({'type': 'Dashboard', 'name': dashboard_name, 'score': round(score, 3)})
    
    # Search in Pages
    pages = frappe.db.sql("SELECT name FROM `tabPage` LIMIT 500", as_list=True)
    for (page_name,) in pages:
        score = similarity_score(unresolved_name, page_name)
        if score > 0.5:
            candidates.append({'type': 'Page', 'name': page_name, 'score': round(score, 3)})
    
    # Sort by score descending, then by type priority (DocType > Report > Dashboard > Page)
    type_priority = {'DocType': 0, 'Report': 1, 'Dashboard': 2, 'Page': 3}
    candidates.sort(key=lambda x: (-x['score'], type_priority.get(x['type'], 99)))
    
    return candidates[:top_n]


def execute():
    """Generate candidate suggestions for Projects workspace unresolved items."""
    
    # Get Projects workspace
    if not frappe.db.exists('Workspace', 'Projects'):
        print(json.dumps({'error': 'Workspace Projects not found'}))
        return
    
    ws = frappe.get_doc('Workspace', 'Projects')
    content_raw = ws.content or ''
    if not content_raw:
        print(json.dumps({'error': 'Workspace Projects has no content'}))
        return
    
    try:
        content = json.loads(content_raw)
    except:
        print(json.dumps({'error': 'Invalid JSON in Projects workspace content'}))
        return
    
    # Extract unresolved items
    unresolved_items = []
    for i, block in enumerate(content):
        if block.get('type') == 'shortcut':
            data = block.get('data') or {}
            unresolved_fields = ['unresolved_shortcut_name', 'shortcut_name']
            for field in unresolved_fields:
                if field in data and data[field]:
                    unresolved_name = data[field]
                    unresolved_items.append({
                        'block_index': i,
                        'unresolved_name': unresolved_name,
                        'field': field
                    })
    
    # Generate candidates for each unresolved item
    results = []
    for item in unresolved_items:
        unresolved_name = item['unresolved_name']
        candidates = find_candidates_for_name(unresolved_name, top_n=5)
        results.append({
            'workspace': 'Projects',
            'block_index': item['block_index'],
            'unresolved_name': unresolved_name,
            'field': item['field'],
            'candidates': candidates
        })
    
    # Save results to file
    output_path = frappe.get_app_path('sigma', 'scripts', 'projects_candidates.json')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(json.dumps({
        'status': 'completed',
        'workspace': 'Projects',
        'unresolved_count': len(unresolved_items),
        'results': results,
        'output_file': output_path
    }))
