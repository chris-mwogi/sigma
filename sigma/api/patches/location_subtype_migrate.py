import frappe


def _ensure_location_subtype(name: str, location_type: str | None = None) -> str:
    if not name:
        return None
    if frappe.db.exists("Location Subtype", name):
        return name
    doc = frappe.new_doc("Location Subtype")
    doc.update({
        "title": name,
        "location_type": location_type or "Substation",
    })
    doc.insert(ignore_permissions=True)
    return doc.name


def run(dry_run: bool = True):
    """One-time data migration: copy Location.substation_type -> Location.location_subtype
    - Creates missing Location Subtype records (defaulting to location_type="Substation")
    - Only updates rows where location_subtype is empty and substation_type is set
    """
    filters = {"substation_type": ("is", "set"), "location_subtype": ("is", "not set")}
    names = frappe.get_all("Location", filters=filters, pluck="name")
    moved = 0
    for name in names:
        doc = frappe.get_doc("Location", name)
        subtype = doc.substation_type
        ltype = getattr(doc, "location_type", None)
        if dry_run:
            print(f"[DRY] Would set location_subtype={subtype} on {name} (type={ltype})")
            continue
        _ensure_location_subtype(subtype, location_type=ltype or "Substation")
        doc.location_subtype = subtype
        doc.save(ignore_permissions=True)
        moved += 1
    print({"total": len(names), "updated": moved, "dry_run": dry_run})

