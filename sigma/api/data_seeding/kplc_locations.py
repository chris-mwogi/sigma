import frappe

# Seed Kenya Power (KPLC) Locations with Region → County → Facility hierarchy
# - Uses Location custom Link fields: location_type (Location Type), location_subtype (Location Subtype)
# - Idempotent: creates missing records; updates core fields if they already exist
# - Source references (for human readers):
#   • KPLC Regional Managers and regions: https://www.kplc.co.ke/regional-managers
#   • Protected Areas (Energy Sector) Order, 2022 (Primary/Distribution Substations by Region/County):
#       https://new.kenyalaw.org/akn/ke/act/ln/2022/39/eng@2022-12-31
#   • KPLC HQ (Stima Plaza) address (site footer): https://www.kplc.co.ke/
#   • Ruaraka Store and KPLC Training School (tender docs):
#       https://www.kplc.co.ke/storage/01JWDGEJRV74N97Z1AARFG2169.pdf
#       https://kplc.co.ke/storage/01JY5X9HG3QW4FP98GG9588BD7.pdf
#   • Mombasa Electricity House (tender doc):
#       https://www.kplc.co.ke/storage/01JMC4QXNFEM4BG7KG6CW32ABR.pdf


def _ensure_master(dt: str, name: str, extra: dict | None = None):
    """Ensure a master/link DocType record exists (Location Type / Location Subtype).
    Returns the record name. Uses title field for these doctypes where name == title.
    """
    if not name:
        return None
    if frappe.db.exists(dt, name):
        return name
    doc = frappe.new_doc(dt)
    # both doctypes use title as naming field
    if "title" in doc.meta.get_fieldnames():
        doc.update({"title": name})
    else:
        doc.update({"name": name})
    if extra:
        doc.update(extra)
    doc.insert(ignore_permissions=True)
    return doc.name


def _get_location_by_name(location_name: str):
    return frappe.db.get_value("Location", {"location_name": location_name}, "name")


def _ensure_location(location_name: str, *, location_type: str, parent: str | None = None,
                      is_group: int = 0, location_subtype: str | None = None,
                      latitude: float | None = None, longitude: float | None = None):
    """Create or update a Location. Returns (name, created: bool)."""
    # ensure link master values exist
    _ensure_master("Location Type", location_type)
    if location_subtype:
        # ensure a Location Subtype exists and is linked to the selected Location Type
        _ensure_master("Location Subtype", location_subtype, extra={"location_type": location_type})

    existing = _get_location_by_name(location_name)
    if existing:
        doc = frappe.get_doc("Location", existing)
        changed = False
        # Update core fields if changed
        if doc.location_type != location_type:
            doc.location_type = location_type; changed = True
        if (getattr(doc, 'location_subtype', None) or None) != (location_subtype or None):
            doc.location_subtype = location_subtype; changed = True
        if (doc.is_group or 0) != (is_group or 0):
            doc.is_group = is_group; changed = True
        if parent and doc.parent_location != parent:
            doc.parent_location = parent; changed = True
        if latitude is not None and doc.latitude != latitude:
            doc.latitude = latitude; changed = True
        if longitude is not None and doc.longitude != longitude:
            doc.longitude = longitude; changed = True
        if changed:
            doc.save(ignore_permissions=True)
        return doc.name, False

    # Create new
    doc = frappe.new_doc("Location")
    doc.update({
        "location_name": location_name,
        "location_type": location_type,
        "parent_location": parent,
        "is_group": is_group,
    })
    if location_subtype:
        doc.location_subtype = location_subtype
    if latitude is not None:
        doc.latitude = latitude
    if longitude is not None:
        doc.longitude = longitude
    doc.insert(ignore_permissions=True)
    return doc.name, True


# Minimal mapping (Region → Counties → Facilities). Substations classified using Kenya Law doc above.
# Keep this dataset reasonably small (< ~200 lines) while covering many regions/counties (30+ facilities).
DATA = {
    "Nairobi Region": {
        "counties": {
            "Nairobi": {
                "facilities": [
                    # Substations (66/11 kV)
                    ("Ruaraka 66/11 kV Substation", "Substation", "66/11 kV"),
                    ("Kileleshwa 66/11 kV Substation", "Substation", "66/11 kV"),
                    ("Nairobi South 66/11 kV Substation", "Substation", "66/11 kV"),
                    ("Parklands 66/11 kV Substation", "Substation", "66/11 kV"),
                    ("Babadogo 66/11 kV Substation", "Substation", "66/11 kV"),
                    ("Eastleigh 66/11 kV Substation", "Substation", "66/11 kV"),
                    ("Airport 66/11 kV Substation", "Substation", "66/11 kV"),
                    ("Karen 66/11 kV Substation", "Substation", "66/11 kV"),
                    ("Langata 66/11 kV Substation", "Substation", "66/11 kV"),
                    ("Ragati 66/11 kV Substation (Upper Hill)", "Substation", "66/11 kV"),
                    # Offices/Stores
                    ("Stima Plaza (Head Office)", "Office", None),
                    ("Ruaraka Store", "Store", None),
                    ("KPLC Training School – Ruaraka", "Office", None),
                ]
            },
            "Machakos": {
                "facilities": [
                    ("Athi River 66/11 kV Substation", "Substation", "66/11 kV"),
                    ("Machakos 33/11 kV Substation", "Substation", "33/11 kV"),
                    ("Syokimau 66/11 kV Substation", "Substation", "66/11 kV"),
                ]
            },
            "Kajiado": {
                "facilities": [
                    ("EPZ 66/11 kV Substation (Kitengela)", "Substation", "66/11 kV"),
                    ("Ngong Town 66/11 kV Substation", "Substation", "66/11 kV"),
                    ("Kajiado 33/11 kV Substation", "Substation", "33/11 kV"),
                ]
            },
        }
    },
    "Coast Region": {
        "counties": {
            "Mombasa": {
                "facilities": [
                    ("Nyali 33/11 kV Substation", "Substation", "33/11 kV"),
                    ("Mbaraki 33/11 kV Substation", "Substation", "33/11 kV"),
                    ("Likoni 33/11 kV Substation", "Substation", "33/11 kV"),
                    ("Miritini 33/11 kV Substation", "Substation", "33/11 kV"),
                    ("Electricity House – Mombasa", "Office", None),
                ]
            },
            "Kilifi": {
                "facilities": [
                    ("Kilifi 33/11 kV Substation", "Substation", "33/11 kV"),
                    ("Malindi 33/11 kV Substation", "Substation", "33/11 kV"),
                    ("Mariakani 33/11 kV Substation", "Substation", "33/11 kV"),
                ]
            },
            "Kwale": {
                "facilities": [
                    ("Diani 33/11 kV Substation", "Substation", "33/11 kV"),
                    ("Msambweni 33/11 kV Substation", "Substation", "33/11 kV"),
                ]
            },
            "Taita Taveta": {
                "facilities": [
                    ("Voi 33/11 kV Substation", "Substation", "33/11 kV"),
                    ("Mwatate 33/11 kV Substation", "Substation", "33/11 kV"),
                ]
            },
            "Lamu": {"facilities": [("Mokowe 33/11 kV Substation", "Substation", "33/11 kV")]},
            "Tana River": {"facilities": [("Hola 33/11 kV Substation", "Substation", "33/11 kV")]},
        }
    },
    "Mt. Kenya Region": {
        "counties": {
            "Embu": {"facilities": [("Embu 33/11 kV Substation", "Substation", "33/11 kV"), ("Embu East 33/11 kV Substation", "Substation", "33/11 kV")]},
            "Meru": {"facilities": [("Meru 33/11 kV Substation", "Substation", "33/11 kV"), ("Kianjai 33/11 kV Substation", "Substation", "33/11 kV")]},
            "Nyeri": {"facilities": [("Nyeri Town (Ruringu) 33/11 kV Substation", "Substation", "33/11 kV"), ("Othaya 33/11 kV Substation", "Substation", "33/11 kV")]},
            "Kirinyaga": {"facilities": [("Kerugoya 33/11 kV Substation", "Substation", "33/11 kV")]},
            "Laikipia": {"facilities": [("Nanyuki 33/11 kV Substation", "Substation", "33/11 kV")]},
            "Murang'a": {"facilities": [("Murang'a 33/11 kV Substation", "Substation", "33/11 kV")]},
        }
    },
    "West Kenya Region": {
        "counties": {
            "Kisumu": {"facilities": [("Kisumu East 33/11 kV Substation", "Substation", "33/11 kV"), ("Kibos 33/11 kV Substation", "Substation", "33/11 kV"), ("Obote 33/11 kV Substation", "Substation", "33/11 kV")]},
            "Kakamega": {"facilities": [("Kakamega 33/11 kV Substation", "Substation", "33/11 kV"), ("Ingotse 33/11 kV Substation", "Substation", "33/11 kV")]},
            "Bungoma": {"facilities": [("Webuye 33/11 kV Substation", "Substation", "33/11 kV"), ("Sibembe 33/11 kV Substation", "Substation", "33/11 kV")]},
            "Busia": {"facilities": [("Busia 33/11 kV Substation", "Substation", "33/11 kV")]},
            "Vihiga": {"facilities": [("Majengo 33/11 kV Substation", "Substation", "33/11 kV")]},
        }
    },
    "South Nyanza Region": {
        "counties": {
            "Kisii": {"facilities": [("Kisii 33/11 kV Substation", "Substation", "33/11 kV"), ("Kisii East 33/11 kV Substation", "Substation", "33/11 kV")]},
            "Homa Bay": {"facilities": [("Homa Bay 33/11 kV Substation", "Substation", "33/11 kV")]},
            "Nyamira": {"facilities": [("Nyamira 33/11 kV Substation", "Substation", "33/11 kV")]},
            "Migori": {"facilities": [("Migori 33/11 kV Substation", "Substation", "33/11 kV"), ("Awendo 33/11 kV Substation", "Substation", "33/11 kV")]},
        }
    },
}


def seed_kplc_locations(dry_run: bool = True):
    """Seed KPLC Locations based on DATA.
    - dry_run=True: only prints actions without writing.
    - dry_run=False: creates/updates records.
    """
    created, updated, skipped = 0, 0, 0

    def do_ensure(loc_name, ltype, parent=None, is_group=0, subtype=None):
        nonlocal created, updated, skipped
        if dry_run:
            print(f"[DRY] Location: {loc_name} | type={ltype} | parent={parent} | group={is_group} | subtype={subtype}")
            skipped += 1
            return None
        name, was_created = _ensure_location(loc_name, location_type=ltype, parent=parent, is_group=is_group, location_subtype=subtype)
        if was_created:
            created += 1
        else:
            updated += 1
        return name

    for region, rdata in DATA.items():
        # Region node
        do_ensure(region, "Region", parent=None, is_group=1)
        for county, cdata in (rdata.get("counties") or {}).items():
            # County node under Region
            do_ensure(county, "County", parent=region, is_group=1)
            for (facility_name, facility_type, substation_kv) in cdata.get("facilities", []):
                do_ensure(facility_name, facility_type, parent=county, is_group=0, subtype=substation_kv)

    print({"created": created, "updated": updated, "skipped": skipped})


# Example usage from bench console:
#   cd ~/frappe-bench && bench --site <yoursite> console
#   In [1]: from sigma.api.data_seeding.kplc_locations import seed_kplc_locations
#   In [2]: seed_kplc_locations(dry_run=True)   # preview
#   In [3]: seed_kplc_locations(dry_run=False)  # apply changes

