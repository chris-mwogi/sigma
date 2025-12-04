import frappe
import json
import re

# Heuristics to generate candidate names from an unresolved label
PREFIXES = ['New ', 'List ', 'All ', 'Recent ', 'View ', 'Create '] 

def singularize(name):
    if name.endswith('ies'):
        return name[:-3] + 'y'
    if name.endswith('s') and not name.endswith('ss'):
        return name[:-1]
    return name

def candidates(name):
    name = (name or '').strip()
    if not name:
        return []
    cands = [name]
    cands.append(name.title())
    cands.append(name.capitalize())
    for p in PREFIXES:
        if name.startswith(p):
            tail = name[len(p):].strip()
            cands.append(tail)
            cands.append(tail.title())
    tokens = name.split()
    if tokens:
        last = tokens[-1]
        s = singularize(last)
        if s != last:
            tokens2 = tokens[:-1] + [s]
            cands.append(' '.join(tokens2))
            cands.append(' '.join(tokens2).title())
    # dedupe
    out = []
    seen = set()
    for c in cands:
        if c and c not in seen:
            seen.add(c)
            out.append(c)
    return out


def search_existing(name):
    """Return list of candidate (type,name) that exist in DB for a name string"""
    results = []
    for c in candidates(name):
        if frappe.db.exists('DocType', c):
            results.append({'type': 'DocType', 'name': c})
        if frappe.db.exists('Report', c):
            results.append({'type': 'Report', 'name': c})
        if frappe.db.exists('Dashboard', c):
            results.append({'type': 'Dashboard', 'name': c})
        if frappe.db.exists('Page', c):
            results.append({'type': 'Page', 'name': c})
    # partial token match fallback
    tokens = re.split(r'\W+', name)
    tokens = [t for t in tokens if t]
    if tokens and not results:
        pattern = '%' + '%'.join(tokens) + '%'
        res = frappe.db.sql("select name from `tabDocType` where name like %s limit 5", (pattern,))
        for r in res:
            results.append({'type': 'DocType', 'name': r[0]})
        res = frappe.db.sql("select name from `tabReport` where name like %s limit 5", (pattern,))
        for r in res:
            results.append({'type': 'Report', 'name': r[0]})
        res = frappe.db.sql("select name from `tabDashboard` where name like %s limit 5", (pattern,))
        for r in res:
            results.append({'type': 'Dashboard', 'name': r[0]})
    # dedupe by (type,name)
    seen = set()
    out = []
    for r in results:
        key = (r['type'], r['name'])
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out


def execute():
    mapping = []
    workspaces = frappe.get_all('Workspace', filters={"module": ["like", "%Sigma%"]}, fields=['name','content'])
    for w in workspaces:
        name = w.get('name')
        content_raw = w.get('content') or ''
        if not content_raw:
            continue
        try:
            content = json.loads(content_raw)
        except Exception:
            continue
        for idx, block in enumerate(content):
            data = block.get('data') or {}
            # check for unresolved markers from auto-fixer
            unresolved = None
            field = None
            if data.get('unresolved_shortcut_name'):
                unresolved = data.get('unresolved_shortcut_name')
                field = 'unresolved_shortcut_name'
            elif data.get('unresolved_link_name'):
                unresolved = data.get('unresolved_link_name')
                field = 'unresolved_link_name'
            elif data.get('shortcut_name'):
                unresolved = data.get('shortcut_name')
                field = 'shortcut_name'
            # also catch opaque-looking values in 'name' for shortcuts/links (IDs like 7u9...)
            elif block.get('type') in ('shortcut','link'):
                candidate_name = data.get('name') or data.get('link_to')
                if candidate_name and re.match(r'^[0-9a-z]{8,}$', candidate_name):
                    unresolved = candidate_name
                    field = 'name'
            if unresolved:
                suggestions = search_existing(unresolved)
                mapping.append({
                    'workspace': name,
                    'block_index': idx,
                    'block_type': block.get('type'),
                    'field': field,
                    'unresolved_name': unresolved,
                    'suggestions': suggestions
                })
    # write mapping file into scripts dir for review
    out_path = frappe.get_app_path('sigma', 'scripts', 'unresolved_mappings.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2)
    print(json.dumps({'mapping_file': out_path, 'entries': len(mapping)}))
