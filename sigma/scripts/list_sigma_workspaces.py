import frappe
import json
import hashlib

def execute():
    rows = []
    for w in frappe.get_all("Workspace", filters={"module": ["like", "%Sigma%"]}, fields=["name","module","content"]):
        content = w.get("content") or ""
        h = hashlib.md5(content.encode("utf-8")).hexdigest()
        rows.append({"name": w.get("name"), "module": w.get("module"), "hash": h, "len": len(content)})
    print(json.dumps(rows))
