# ⚙️ Sigma Case Management — ERPNext Module

**Module Path:** `sigma/sigma/sigma_case_management/`  
**Maintained by:** Prismod Technologies Limited  
**Description:** Case Management System for Power Utility Company (KPLC-style) — covering theft handling, incidents, prosecutions, and departmental coordination.

---

## 📂 Folder Structure

```
sigma/
 └── sigma/
      └── sigma_case_management/
           ├── __init__.py
           ├── hooks.py
           ├── config/
           │    └── desktop.py
           ├── doctype/
           │    └── case/
           │         ├── __init__.py
           │         ├── case.json
           │         └── case.py
           ├── fixtures/
           │    ├── workflow.json
           │    ├── role.json
           │    ├── custom_field.json
           │    └── property_setter.json
           └── public/
                ├── js/
                │    └── case_dashboard.js
                └── css/
                     └── case.css
```

---

## 📘 Fixtures

### 1. Workflow (`workflow.json`)
Defines the lifecycle of a Case:

| State | Editable By | Next Action | Next State |
|--------|--------------|--------------|-------------|
| Open | Security Officer | Start Investigation | In Investigation |
| In Investigation | Security Officer | Forward to Legal | Awaiting Legal |
| Awaiting Legal | Legal Officer | Resolve | Resolved |
| Resolved | Security Officer | Close Case | Closed |

---

### 2. Roles (`role.json`)
| Role | Description |
|------|--------------|
| Security Officer | Handles case reporting and initial investigation |
| Case Supervisor | Oversees escalations and investigation process |
| Legal Officer | Handles prosecution and legal closure |

---

### 3. Custom Field (`custom_field.json`)
| Fieldname | Label | Type | Linked To | Description |
|------------|--------|------|------------|-------------|
| `asset_link` | Related Asset | Link | Asset | Connects a Case to an ERPNext Asset record |

---

### 4. Property Setters (`property_setter.json`)
Customizes standard ERPNext doctypes:

| Doctype | Field | Change | New Value | Description |
|----------|--------|---------|------------|-------------|
| Asset | location | reqd | 1 | Make Asset location mandatory for theft tracking |
| Issue | category | label | Incident Type | Rename for incident reporting |
| Asset | status | options | Draft, In Use, Under Maintenance, Under Investigation, Scrapped | Adds “Under Investigation” option |

```json
[
  {
    "doctype": "Property Setter",
    "doctype_or_field": "DocField",
    "doc_type": "Asset",
    "field_name": "location",
    "property": "reqd",
    "property_type": "Check",
    "value": "1"
  },
  {
    "doctype": "Property Setter",
    "doctype_or_field": "DocField",
    "doc_type": "Issue",
    "field_name": "category",
    "property": "label",
    "property_type": "Data",
    "value": "Incident Type"
  },
  {
    "doctype": "Property Setter",
    "doctype_or_field": "DocField",
    "doc_type": "Asset",
    "field_name": "status",
    "property": "options",
    "property_type": "Text",
    "value": "Draft\nIn Use\nUnder Maintenance\nUnder Investigation\nScrapped"
  }
]
```

---

## ⚙️ `hooks.py`
```python
from . import __version__ as app_version

app_name = "sigma"
app_title = "Sigma"
app_publisher = "Nevel Enterprises Limited"
app_description = "Case Management for Power Utility Security Department"
app_icon = "octicon octicon-shield"
app_color = "blue"
app_email = "support@nevel.co.ke"
app_license = "MIT"

fixtures = [
    {"doctype": "Workflow", "filters": [["name", "in", ["Case Workflow"]]]},
    {"doctype": "Role", "filters": [["name", "in", ["Security Officer", "Legal Officer", "Case Supervisor"]]]},
    {"doctype": "Custom Field", "filters": [["dt", "=", "Case"]]},
    {"doctype": "Property Setter", "filters": [["doc_type", "in", ["Asset", "Issue"]]]}
]
```

---

## 🧭 Installation

```bash
cd ~/frappe-bench/apps/sigma
unzip /path/to/sigma_case_management_with_fixtures.zip -d .
bench migrate
bench clear-cache
```

---

## 🧪 Optional: Sample Case Data

| Case Type | Description | Related Asset | Status |
|------------|--------------|----------------|---------|
| Fuel Theft | Unauthorized fuel siphoning from generator | Asset-001 | In Investigation |
| Meter Tampering | Smart meter bypass at depot | Asset-019 | Awaiting Legal |
| Substation Fire Drill | Scheduled drill with KPLC Fire Unit | N/A | Resolved |

---

## 🧰 Maintainers

**Nevel Enterprises Limited**  
📧 support@nevel.co.ke  
📍 Nairobi, Kenya
