# 🧩 Sigma Integrations
**Unified Asset Integrations for ERPNext**  
© 2025 Prismod Technologies Limited / Nevel Enterprises

---

## 📘 Overview
**Sigma Integrations** extends ERPNext with real-time asset monitoring capabilities by integrating data from IoT devices, network monitors (like ManageEngine OpManager), and unified telemetry feeds.

It enables seamless visualization of asset location, telemetry (IoT readings), and alarm states directly within ERPNext dashboards (e.g., *Tracking Dashboard* or *Asset Analytics*).

---

## 🔌 Modules Included

### 1. `iot_asset_integrations_api.py`
**Purpose:**  
Interfaces with IoT platforms or MQTT brokers to ingest telemetry data into ERPNext.  
Typically handles metrics like **liquid level**, **temperature**, **battery voltage**, or **signal strength**.

**Example Endpoint:**
```python
@frappe.whitelist(allow_guest=True)
def receive_iot_data(asset_tag, payload_json):
    """
    Receives JSON payload from IoT device and logs data
    into `Asset Data Log`.
    """
```

**Expected Payload Example:**
```json
{
  "asset_tag": "GEN-001",
  "liquid_level": 85.2,
  "temperature": 32.5,
  "battery": 12.1,
  "signal": -67
}
```

---

### 2. `opmanager_asset_monitor_api.py`
**Purpose:**  
Connects ERPNext to **OpManager** (or similar network monitoring tools).  
Pulls or receives network alarms and device statuses to associate them with ERPNext **Assets**.

**Sample Function:**
```python
@frappe.whitelist()
def get_tracking_data():
    """
    Returns asset data (with category icons) for the tracking dashboard.
    """
```

**Returns:**  
- Asset name, category, icon, location (lat/lon), and alarm state.  
- Used by `tracking-dashboard` page to render markers on the map.

---

### 3. `unified_asset_stream_api.py`
**Purpose:**  
Provides a single unified API that merges data from IoT devices and OpManager into a comprehensive asset feed.

**Endpoints:**

#### `get_unified_assets()`
Returns all active assets with:
- Category icon
- Last known location
- Last seen timestamp
- Latest alarm info

#### `get_asset_trend(asset_name)`
Returns time-series telemetry for a single asset, such as:
- Speed
- Liquid level
- Temperature
- Battery
- Signal

**Output Example:**
```json
{
  "asset_name": "GEN-001",
  "latitude": "-1.2987",
  "longitude": "36.8123",
  "last_alarm": "Fuel Leak Detected",
  "last_alarm_time": "2025-10-16 08:42:00"
}
```

---

## 🏗️ Installation

1. Copy or extract the `sigma_integrations` module into your Sigma app:
   ```bash
   cd apps/sigma/sigma/
   mkdir -p sigma_integrations/api
   ```

2. Add the files:
   - `iot_asset_integrations_api.py`
   - `opmanager_asset_monitor_api.py`
   - `unified_asset_stream_api.py`

3. Update `hooks.py` to include API imports if necessary:
   ```python
   app_include_js = [
       "/assets/sigma/js/tracking-dashboard.js"
   ]
   ```

4. Run migrations and restart bench:
   ```bash
   bench migrate
   bench restart
   ```

---

## 🔄 Data Flow Summary

| Source | Entry Point | ERPNext Target | Description |
|--------|-------------|----------------|-------------|
| IoT Gateway | `/api/method/sigma_integrations.api.iot_asset_integrations_api.receive_iot_data` | `Asset Data Log` | Logs telemetry readings |
| OpManager | `/api/method/sigma_integrations.api.opmanager_asset_monitor_api.receive_opmanager_alert` | `Asset` | Logs network alarms |
| Unified API | `/api/method/sigma_integrations.api.unified_asset_stream_api.get_unified_assets` | Dashboard | Aggregates all data for visualization |

---

## 🛠️ Dependencies
- ERPNext v15+
- Python 3.10+
- Frappe Framework v15+
- Valid `Asset` and `Asset Category` doctypes
- Optional: `Asset Data Log` custom doctype

---

## 📡 Example Use Case
- IoT device reports **fuel level** every 5 minutes.
- OpManager flags a **device offline** alert.
- ERPNext dashboard shows both the **fuel trend** and **connectivity status** of the same generator asset.
