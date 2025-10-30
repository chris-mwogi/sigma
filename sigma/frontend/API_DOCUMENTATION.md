# Sigma Frontend - API Documentation

This document describes all API endpoints used by the Sigma Vue.js frontend.

## Base URL

All API calls are made to the Frappe backend at:
```
http://prismod.co.ke/api
```

## Authentication

All requests include:
- **CSRF Token**: Automatically added from cookies
- **Session Cookie**: Maintained by browser
- **Content-Type**: `application/json`

## API Endpoints

### Authentication

#### Get Current User
```
GET /api/method/frappe.auth.get_logged_user
```
Returns the email of the currently logged-in user.

#### Login
```
POST /api/method/frappe.client.login
Body: {
  "usr": "user@example.com",
  "pwd": "password"
}
```
Authenticates user and creates session.

#### Logout
```
POST /api/method/frappe.client.logout
```
Destroys user session.

### Cases

#### List Cases
```
GET /api/resource/Case
Query Parameters:
  - fields: ["name","title","status","modified"]
  - limit_page_length: 500
  - order_by: `modified` desc
```
Returns array of case objects.

**Response:**
```json
{
  "data": [
    {
      "name": "CASE-001",
      "title": "Security Breach Investigation",
      "status": "Open",
      "modified": "2024-01-15T10:30:00"
    }
  ]
}
```

#### Get Case Details
```
GET /api/resource/Case/{case_id}
```
Returns full case object with all fields.

#### Create Case
```
POST /api/resource/Case
Body: {
  "title": "Case Title",
  "description": "Case description",
  "priority": "High",
  "status": "Open",
  "assigned_to": "user@example.com"
}
```
Creates new case and returns created object.

### Incidents

#### List Incidents
```
GET /api/resource/Incident Report
Query Parameters:
  - fields: ["name","title","incident_date","status"]
  - limit_page_length: 500
```
Returns array of incident objects.

#### Get Incident Details
```
GET /api/resource/Incident Report/{incident_id}
```
Returns full incident object.

### Access Control

#### List Access Events
```
GET /api/resource/Access Event
Query Parameters:
  - fields: ["name","title","creation"]
  - limit_page_length: 100
```

#### List Access Points
```
GET /api/resource/Access Point
Query Parameters:
  - fields: ["name","title","creation"]
  - limit_page_length: 100
```

#### List Access Policies
```
GET /api/resource/Access Policy
Query Parameters:
  - fields: ["name","title","creation"]
  - limit_page_length: 100
```

### Guard Monitoring

#### List Guard Shifts
```
GET /api/resource/Guard Shift
Query Parameters:
  - fields: ["name","guard_name","shift_date","start_time","end_time","status"]
  - limit_page_length: 100
```

### Assets

#### List Assets
```
GET /api/resource/Asset
Query Parameters:
  - fields: ["name","asset_name","asset_type","status","asset_value"]
  - limit_page_length: 500
```

#### Get Asset Details
```
GET /api/resource/Asset/{asset_id}
```
Returns full asset object with all fields.

### Risk Assessment

#### List Risk Assessments
```
GET /api/resource/Risk Assessment
Query Parameters:
  - fields: ["name","title","risk_level","status","assessment_date"]
  - limit_page_length: 100
```

## Response Format

### Success Response
```json
{
  "data": {
    "name": "DOC-001",
    "title": "Document Title",
    ...
  }
}
```

### Error Response
```json
{
  "exc": "[\"ValidationError\"]",
  "message": "Error message describing what went wrong"
}
```

## Common Query Parameters

- **fields**: Array of field names to return
- **limit_page_length**: Number of records to return (default: 20)
- **limit_start**: Offset for pagination
- **order_by**: Field to sort by (e.g., `modified` desc)
- **filters**: Array of filter conditions

## Error Codes

- **401**: Unauthorized - User not logged in
- **403**: Forbidden - User lacks permission
- **404**: Not Found - Resource doesn't exist
- **422**: Validation Error - Invalid data
- **500**: Server Error - Backend error

## Rate Limiting

No explicit rate limiting is enforced, but excessive requests may be throttled.

## CORS

CORS is handled by Frappe. The frontend is served from the same domain as the API.

## Pagination

For large datasets, use pagination:
```
GET /api/resource/Case?limit_page_length=10&limit_start=0
```

## Filtering

Filter by field value:
```
GET /api/resource/Case?filters=[["status","=","Open"]]
```

Multiple filters (AND):
```
GET /api/resource/Case?filters=[["status","=","Open"],["priority","=","High"]]
```

## Sorting

Sort by field:
```
GET /api/resource/Case?order_by=`modified` desc
```

## Field Selection

Return only specific fields:
```
GET /api/resource/Case?fields=["name","title","status"]
```

## Examples

### Get all open cases
```
GET /api/resource/Case?filters=[["status","=","Open"]]&fields=["name","title","status"]
```

### Get recent incidents (last 7 days)
```
GET /api/resource/Incident Report?filters=[["incident_date",">=",DATE_7_DAYS_AGO]]&order_by=`incident_date` desc
```

### Get active guard shifts
```
GET /api/resource/Guard Shift?filters=[["status","=","Active"]]
```

## Caching

The frontend caches data in Pinia stores. To refresh:
- Call the load function again
- Use the refresh button in the UI
- Data is automatically refreshed on page navigation

## WebSocket Events

Real-time updates are available through Frappe's WebSocket:
- Case updates
- Incident notifications
- Access events
- Guard location updates

(Implementation details in `src/services/realtime.js`)

## Rate Limiting Best Practices

- Debounce search queries
- Paginate large datasets
- Cache frequently accessed data
- Use field selection to reduce payload size

## Support

For API issues, check:
1. Browser console for errors
2. Network tab for request/response details
3. Frappe server logs
4. Contact: info@prismod.co.ke

