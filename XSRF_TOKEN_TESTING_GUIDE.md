# XSRF-TOKEN Fix - Testing Guide

## Quick Test Checklist

### ✅ Step 1: Access Frontend
```
URL: https://prismod.co.ke/sigma-frontend
Expected: Page loads without errors
```

### ✅ Step 2: Check Meta Tag
Open browser console (F12) and run:
```javascript
document.querySelector('meta[name="csrf-token"]').getAttribute('content')
```
**Expected**: Returns a token value (e.g., `abc123def456...`)

### ✅ Step 3: Check Cookies
In browser console:
```javascript
document.cookie
```
**Expected**: Should contain `frappe_csrf_token=...`

### ✅ Step 4: Check API Service
In browser console:
```javascript
// Import the API service
import api from '/assets/sigma/dist/js/index.js'
// Make a test request
api.get('/api/resource/User').then(r => console.log('Success:', r)).catch(e => console.log('Error:', e))
```
**Expected**: Request succeeds or shows meaningful error (not XSRF-TOKEN error)

### ✅ Step 5: Check Network Tab
1. Open DevTools (F12)
2. Go to Network tab
3. Make an API request from the frontend
4. Click on the request
5. Go to Headers tab
6. Look for `X-Frappe-CSRF-Token` header

**Expected**: Header is present with token value

## Detailed Testing

### Test 1: Token Availability

**Objective**: Verify CSRF token is available to frontend

**Steps**:
1. Open `https://prismod.co.ke/sigma-frontend`
2. Open browser console (F12)
3. Run: `document.querySelector('meta[name="csrf-token"]').getAttribute('content')`

**Expected Result**:
```
"abc123def456ghi789jkl012mno345pqr678stu901vwx234yz"
```

**If Failed**:
- Check if page is fully loaded
- Check if meta tag exists: `document.querySelector('meta[name="csrf-token"]')`
- Check HTML source for meta tag

### Test 2: Cookie Availability

**Objective**: Verify CSRF token cookie is set

**Steps**:
1. Open browser console
2. Run: `document.cookie`

**Expected Result**:
```
"frappe_csrf_token=abc123def456...; other_cookies=..."
```

**If Failed**:
- Check if session is valid
- Check if cookies are enabled
- Try clearing cookies and reloading

### Test 3: API Request with Token

**Objective**: Verify token is sent in API requests

**Steps**:
1. Open DevTools (F12)
2. Go to Network tab
3. Open browser console
4. Run: `fetch('/api/resource/User', {method: 'GET', credentials: 'include'})`
5. Check the request in Network tab

**Expected Result**:
- Request headers include: `X-Frappe-CSRF-Token: abc123def456...`
- Response status: 200 (not 403)

**If Failed**:
- Check if token is being sent
- Check if token value is correct
- Check server logs for errors

### Test 4: Form Submission

**Objective**: Verify token works with form submissions

**Steps**:
1. In browser console, run:
```javascript
const api = axios.create({
  baseURL: window.location.origin,
  withCredentials: true
})
api.post('/api/resource/User', {
  email: 'test@example.com'
}).then(r => console.log('Success:', r)).catch(e => console.log('Error:', e))
```

**Expected Result**:
- Request succeeds (or shows meaningful error, not XSRF-TOKEN error)
- Response status: 200 or 201

**If Failed**:
- Check if token is being sent
- Check if token is valid
- Check server logs

### Test 5: Multiple Requests

**Objective**: Verify token works for multiple requests

**Steps**:
1. Make 5 consecutive API requests
2. Check that all succeed

**Expected Result**:
- All requests succeed
- No XSRF-TOKEN errors

**If Failed**:
- Check if token is being refreshed
- Check if session is expiring
- Check server logs

## Browser Console Commands

### Get CSRF Token
```javascript
document.querySelector('meta[name="csrf-token"]').getAttribute('content')
```

### Get CSRF Cookie
```javascript
document.cookie.split(';').find(c => c.includes('frappe_csrf_token'))
```

### Test API Request
```javascript
fetch('/api/resource/User', {
  method: 'GET',
  credentials: 'include',
  headers: {
    'X-Frappe-CSRF-Token': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
  }
}).then(r => r.json()).then(d => console.log(d)).catch(e => console.log(e))
```

### Check Request Headers
```javascript
// In Network tab, click on request, go to Headers tab
// Look for: X-Frappe-CSRF-Token
```

## Common Issues & Solutions

### Issue 1: Meta Tag Not Found
**Error**: `Cannot read property 'getAttribute' of null`

**Solution**:
1. Check if page is fully loaded
2. Check HTML source for meta tag
3. Reload page
4. Check Python handler is passing token

### Issue 2: Token is Null/Undefined
**Error**: `X-Frappe-CSRF-Token: null`

**Solution**:
1. Check if session is valid
2. Check if cookies are enabled
3. Check if meta tag has content
4. Clear cookies and reload

### Issue 3: XSRF-TOKEN Error Still Occurring
**Error**: `403 Forbidden - XSRF-TOKEN error`

**Solution**:
1. Verify token is being sent in headers
2. Verify token value matches server-side
3. Check if session is valid
4. Check server logs for errors

### Issue 4: Token Mismatch
**Error**: `403 Forbidden - Token mismatch`

**Solution**:
1. Clear browser cookies
2. Reload page
3. Check if token is being regenerated
4. Check server logs

## Performance Testing

### Test 1: Token Retrieval Speed
```javascript
console.time('getToken')
const token = document.querySelector('meta[name="csrf-token"]').getAttribute('content')
console.timeEnd('getToken')
```
**Expected**: < 1ms

### Test 2: Request Speed with Token
```javascript
console.time('apiRequest')
fetch('/api/resource/User', {
  method: 'GET',
  credentials: 'include',
  headers: {
    'X-Frappe-CSRF-Token': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
  }
}).then(r => {
  console.timeEnd('apiRequest')
  return r.json()
}).then(d => console.log(d))
```
**Expected**: < 500ms

## Verification Checklist

- [ ] Meta tag exists in HTML
- [ ] Meta tag has content (token value)
- [ ] Cookie `frappe_csrf_token` is set
- [ ] Token is sent in request headers
- [ ] API requests succeed
- [ ] No XSRF-TOKEN errors in console
- [ ] No XSRF-TOKEN errors in server logs
- [ ] Multiple requests work
- [ ] Token works for different endpoints
- [ ] Performance is acceptable

## Success Criteria

✅ **All of the following must be true**:
1. Meta tag contains token value
2. Cookie is set correctly
3. Token is sent in all requests
4. API requests succeed
5. No XSRF-TOKEN errors
6. Performance is good

## Next Steps

If all tests pass:
1. ✅ XSRF-TOKEN fix is working
2. ✅ Frontend is ready for production
3. ✅ Deploy to production

If any test fails:
1. ❌ Check troubleshooting section
2. ❌ Review error messages
3. ❌ Check server logs
4. ❌ Contact support

---

**Last Updated**: 2025-10-28
**Status**: Ready for Testing

