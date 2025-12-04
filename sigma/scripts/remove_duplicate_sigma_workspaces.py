import frappe
import json

def execute():
    # Find all Sigma workspaces
    workspaces = frappe.get_all("Workspace", filters={"module": ["like", "%Sigma%"]}, fields=["name","module","content"])
    # group by hash
    import hashlib
    groups = {}
    for w in workspaces:
        content = w.get("content") or ""
        h = hashlib.md5(content.encode('utf-8')).hexdigest()
        groups.setdefault(h, []).append({"name": w.get("name"), "module": w.get("module"), "len": len(content)})

    to_delete = []
    for h, items in groups.items():
        if len(items) <= 1:
            continue
        # If there exists a pair of "Name" and "Sigma Name", delete "Sigma Name"
        names = [i['name'] for i in items]
        deleted_in_group = set()
        for n in names:
            if n.startswith('Sigma '):
                plain = n[len('Sigma '):]
                if plain in names:
                    to_delete.append(n)
                    deleted_in_group.add(n)
        # For remaining duplicates (same content but no Sigma prefix pair), keep longest and delete others
        remaining = [i for i in items if i['name'] not in deleted_in_group]
        if len(remaining) > 1:
            # sort descending by len and keep first
            remaining_sorted = sorted(remaining, key=lambda x: x['len'], reverse=True)
            keeper = remaining_sorted[0]['name']
            for rem in remaining_sorted[1:]:
                # avoid double-deleting
                if rem['name'] not in to_delete:
                    to_delete.append(rem['name'])

    # Deduplicate list
    to_delete = list(dict.fromkeys(to_delete))
    print(json.dumps({"to_delete": to_delete}))

    # Perform deletion
    for name in to_delete:
        try:
            # use force to bypass standard checks
            frappe.delete_doc("Workspace", name, force=True)
            print(json.dumps({"deleted": name}))
        except Exception as e:
            print(json.dumps({"error": name, "msg": str(e)}))
