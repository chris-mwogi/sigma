import frappe
import json
import os


def apply_mapping_entry_to_workspace(ws_name, unresolved, block_type, suggestion, diagnostics):
    """Find matching block(s) in workspace content by unresolved name and apply suggestion."""
    ws = frappe.get_doc('Workspace', ws_name)
    content_raw = ws.content or ''
    if not content_raw:
        return False, 'empty_content'
    try:
        content = json.loads(content_raw)
    except Exception as e:
        return False, f'invalid_json:{e}'

    applied = False
    changed_notes = []
    # Search blocks for a match — prefer blocks with unresolved markers
    for i, block in enumerate(content):
        if block.get('type') != block_type:
            continue
        data = block.get('data') or {}
        # check unresolved markers or legacy keys or opaque name
        candidates = []
        if data.get('unresolved_shortcut_name'):
            candidates.append(data.get('unresolved_shortcut_name'))
        if data.get('unresolved_link_name'):
            candidates.append(data.get('unresolved_link_name'))
        if data.get('shortcut_name'):
            candidates.append(data.get('shortcut_name'))
        # name/link_to fields might be the opaque id too
        if data.get('name'):
            candidates.append(data.get('name'))
        if data.get('link_to'):
            candidates.append(data.get('link_to'))

        # normalize and compare
        found = any((c == unresolved) for c in candidates if c is not None)
        if not found:
            continue

        # apply suggestion
        t = suggestion.get('type')
        n = suggestion.get('name')
        if not t or not n:
            diagnostics.append({'workspace': ws_name, 'block_index': i, 'problem': 'invalid_suggestion', 'suggestion': suggestion})
            continue

        # set fields
        data['type'] = t
        data['link_to'] = n
        data['name'] = n
        if not data.get('label'):
            data['label'] = unresolved
        # remove legacy/unresolved keys
        for k in ['unresolved_shortcut_name', 'unresolved_link_name', 'shortcut_name']:
            if k in data:
                del data[k]
        block['data'] = data
        content[i] = block
        applied = True
        changed_notes.append({'index': i, 'from': unresolved, 'to': {'type': t, 'name': n}})
        # don't break: there may be duplicates in a workspace; continue to replace all

    if applied:
        # backup current content to site files
        backup_dir = os.path.join(frappe.get_site_path(), 'public', 'files', 'workspace_backups', 'apply_single')
        os.makedirs(backup_dir, exist_ok=True)
        backup_file = os.path.join(backup_dir, f"{ws_name.replace(' ','_')}.json")
        with open(backup_file + '.before', 'w', encoding='utf-8') as f:
            f.write(content_raw)

        ws.content = json.dumps(content)
        ws.save()

        with open(backup_file + '.after', 'w', encoding='utf-8') as f:
            f.write(ws.content or '')

        return True, changed_notes
    else:
        return False, 'no_matching_block_found'


def execute():
    mapping_path = frappe.get_app_path('sigma', 'scripts', 'unresolved_mappings.json')
    if not os.path.exists(mapping_path):
        print(json.dumps({'error': 'mapping_file_not_found', 'path': mapping_path}))
        return
    with open(mapping_path, 'r', encoding='utf-8') as f:
        mapping = json.load(f)

    applied = []
    skipped = []
    diagnostics = []
    for entry in mapping:
        suggestions = entry.get('suggestions') or []
        if len(suggestions) != 1:
            skipped.append({'workspace': entry.get('workspace'), 'unresolved': entry.get('unresolved_name'), 'reason': 'not_single_suggestion', 'count': len(suggestions)})
            continue
        suggestion = suggestions[0]
        ws_name = entry.get('workspace')
        unresolved = entry.get('unresolved_name')
        block_type = entry.get('block_type')
        ok, info = apply_mapping_entry_to_workspace(ws_name, unresolved, block_type, suggestion, diagnostics)
        if ok:
            applied.append({'workspace': ws_name, 'unresolved': unresolved, 'applied': info})
        else:
            skipped.append({'workspace': ws_name, 'unresolved': unresolved, 'reason': info})

    result = {'applied_count': len(applied), 'skipped_count': len(skipped), 'applied': applied, 'skipped': skipped, 'diagnostics': diagnostics}
    print(json.dumps(result))
