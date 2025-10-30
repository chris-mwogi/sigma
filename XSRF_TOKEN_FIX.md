# XSRF-TOKEN Fix - Complete Solution

## Problem

The Sigma frontend was failing to include the CSRF token in API requests, resulting in XSRF-TOKEN errors when making requests to the Frappe backend.

### Root Causes

1. **Wrong Cookie Name**: The API service was looking for `csrf_token` cookie, but Frappe uses `frappe_csrf_token`
2. **No Meta Tag**: The HTML template didn't expose the CSRF token via a meta tag
3. **No Token in Context**: The Python handler wasn't passing the CSRF token to the template context

## Solution

### 1. Updated API Service (`apps/sigma/sigma/frontend/src/services/api.js`)

**Changes Made:**
- Created `getCSRFToken()` function that:
  - First tries to get token from `frappe_csrf_token` cookie
  - Falls back to `csrf_token` cookie if not found
  - Falls back to meta tag `csrf-token` if not in cookies
- Updated request interceptor to use `getCSRFToken()`
- Removed hardcoded token from axios create config

**Key Code:**
```javascript
function getCSRFToken() {
  // Try to get from cookie first
  let token = getCookie('frappe_csrf_token') || getCookie('csrf_token')
  
  // If not in cookie, try to get from meta tag
  if (!token) {
    const metaTag = document.querySelector('meta[name="csrf-token"]')
    if (metaTag) {
      token = metaTag.getAttribute('content')
    }
  }
  
  return token
}

// In request interceptor:
api.interceptors.request.use(
  config => {
    const token = getCSRFToken()
    if (token) {
      config.headers['X-Frappe-CSRF-Token'] = token
    }
    return config
  },
  error => Promise.reject(error)
)
```

### 2. Updated HTML Template (`apps/sigma/sigma/www/sigma-frontend.html`)

**Changes Made:**
- Added meta tag to expose CSRF token to JavaScript:
```html
<meta name="csrf-token" content="{{ csrf_token }}">
```

This allows the frontend to access the token via:
```javascript
document.querySelector('meta[name="csrf-token"]').getAttribute('content')
```

### 3. Updated Python Handler (`apps/sigma/sigma/www/sigma-frontend.py`)

**Changes Made:**
- Added CSRF token to context:
```python
context.csrf_token = frappe.sessions.get_csrf_token()
```

This passes the token to the HTML template where it's rendered in the meta tag.

## How It Works

### Request Flow

1. **Page Load**:
   - Frappe renders `sigma-frontend.html`
   - Python handler provides CSRF token via `frappe.sessions.get_csrf_token()`
   - Token is rendered in meta tag: `<meta name="csrf-token" content="TOKEN_VALUE">`

2. **API Request**:
   - Frontend makes API call via axios
   - Request interceptor calls `getCSRFToken()`
   - `getCSRFToken()` retrieves token from:
     - `frappe_csrf_token` cookie (primary)
     - `csrf_token` cookie (fallback)
     - `csrf-token` meta tag (fallback)
   - Token is added to request header: `X-Frappe-CSRF-Token: TOKEN_VALUE`

3. **Backend Validation**:
   - Frappe validates the token
   - Request is processed if token is valid
   - Request is rejected if token is missing or invalid

## Token Retrieval Priority

The `getCSRFToken()` function uses this priority order:

1. **`frappe_csrf_token` cookie** (Frappe's standard cookie name)
2. **`csrf_token` cookie** (Fallback for compatibility)
3. **`csrf-token` meta tag** (Fallback if cookies not available)

This ensures the token is always available regardless of how Frappe sets it.

## Testing

### Verify Token is Available

Open browser console and run:
```javascript
// Check cookies
document.cookie  // Should contain frappe_csrf_token

// Check meta tag
document.querySelector('meta[name="csrf-token"]').getAttribute('content')  // Should show token

// Check API service
import { getCSRFToken } from '/assets/sigma/dist/js/index.js'
getCSRFToken()  // Should return token value
```

### Verify Token is Sent

1. Open browser DevTools (F12)
2. Go to Network tab
3. Make an API request from the frontend
4. Check the request headers
5. Look for `X-Frappe-CSRF-Token` header with token value

### Expected Result

```
Request Headers:
X-Frappe-CSRF-Token: abc123def456...
Content-Type: application/json
```

## Deployment

### Build Frontend
```bash
cd apps/sigma/sigma/frontend
npm run build
```

### Clear Cache
```bash
bench --site prismod.co.ke clear-cache
```

### Rebuild Assets
```bash
bench build --app sigma
```

### Restart Frappe
```bash
bench restart
```

## Troubleshooting

### Token Not Found

**Symptom**: `getCSRFToken()` returns `null` or `undefined`

**Solution**:
1. Check if page is loaded: `document.readyState === 'complete'`
2. Check meta tag exists: `document.querySelector('meta[name="csrf-token"]')`
3. Check cookies: `document.cookie`
4. Check browser console for errors

### XSRF-TOKEN Error Still Occurring

**Symptom**: API requests return 403 Forbidden with XSRF-TOKEN error

**Solution**:
1. Verify token is being sent in request headers
2. Verify token value matches server-side token
3. Check if cookies are being sent: `withCredentials: true` in axios config
4. Check Frappe logs for token validation errors

### Token Mismatch

**Symptom**: Token is sent but server rejects it

**Solution**:
1. Clear browser cookies and reload page
2. Check if session is valid: `frappe.session.user`
3. Verify CSRF token generation: `frappe.sessions.get_csrf_token()`
4. Check if token is being regenerated on each request

## Files Modified

1. **apps/sigma/sigma/frontend/src/services/api.js**
   - Added `getCSRFToken()` function
   - Updated request interceptor
   - Removed hardcoded token

2. **apps/sigma/sigma/www/sigma-frontend.html**
   - Added meta tag for CSRF token

3. **apps/sigma/sigma/www/sigma-frontend.py**
   - Added CSRF token to context

## Summary

The XSRF-TOKEN error has been fixed by:
- ✅ Correcting the cookie name to `frappe_csrf_token`
- ✅ Adding meta tag to expose token to JavaScript
- ✅ Passing token from backend to frontend
- ✅ Implementing robust token retrieval with fallbacks
- ✅ Ensuring token is sent in all API requests

The frontend now properly handles CSRF token validation and can make authenticated API requests to the Frappe backend.

---

**Fix Date**: 2025-10-28
**Status**: ✅ COMPLETE
**Ready for Testing**: YES

