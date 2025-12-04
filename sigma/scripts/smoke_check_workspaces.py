import frappe
import json

VALID_TYPES = {
    'DocType': 'DocType',
    'Report': 'Report',
    'Dashboard': 'Dashboard',
    'Page': 'Page'
}

def check_reference(ref_type, name):
    doctype = VALID_TYPES.get(ref_type)
    if not doctype:
        # Unknown reference type; assume OK but flag as unknown
        return {'ok': True, 'note': f'unknown_ref_type:{ref_type}'}
    try:
        exists = frappe.db.exists(doctype, name)
        return {'ok': bool(exists), 'exists': bool(exists)}
    except Exception as e:
        return {'ok': False, 'error': str(e)}


def validate_block(block):
    issues = []
    btype = block.get('type')
    data = block.get('data') or {}

    # shortcut blocks usually have type DocType references in data.link_to or data.name
    if btype == 'shortcut':
        name = data.get('link_to') or data.get('name')
        ref_type = data.get('type') or 'DocType'
        res = check_reference(ref_type, name)
        if not res.get('ok'):
            issues.append({'block': block, 'problem': f"missing {ref_type} {name}", 'detail': res})
    elif btype == 'link':
        name = data.get('link_to') or data.get('name')
        ref_type = data.get('type') or 'DocType'
        res = check_reference(ref_type, name)
        if not res.get('ok'):
            issues.append({'block': block, 'problem': f"missing {ref_type} {name}", 'detail': res})
    elif btype == 'card':
        # cards are presentation only; check if card_name matches a Dashboard or Report optionally
        card_name = data.get('card_name')
        # Try Dashboard then Report
        if card_name:
            if not frappe.db.exists('Dashboard', card_name) and not frappe.db.exists('Report', card_name):
                # not necessarily an issue, but warn
                issues.append({'block': block, 'problem': f"card_name '{card_name}' not a Dashboard or Report"})
    # number cards etc can be ignored for now
    return issues


def execute():
    out = []
    workspaces = frappe.get_all('Workspace', filters={"module": ["like", "%Sigma%"]}, fields=['name','content'])
    for w in workspaces:
        name = w.get('name')
        content_raw = w.get('content') or ''
        workspace_report = {'workspace': name, 'issues': []}
        if not content_raw:
            workspace_report['issues'].append({'problem': 'empty_content'})
            out.append(workspace_report)
            continue
        try:
            content = json.loads(content_raw)
        except Exception as e:
            workspace_report['issues'].append({'problem': 'invalid_json', 'error': str(e)})
            out.append(workspace_report)
            continue
        # Validate each block
        for block in content:
            issues = validate_block(block)
            if issues:
                workspace_report['issues'].extend(issues)
        out.append(workspace_report)

    # Summarize
    summary = {'total': len(out), 'workspaces_with_issues': sum(1 for r in out if r['issues']), 'details': out}
    print(json.dumps(summary, indent=None))
