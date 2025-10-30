# Sigma Frontend - Testing Guide

Complete guide for testing the deployed Sigma Vue.js frontend application.

---

## 🚀 Pre-Testing Checklist

Before testing, ensure:
- [ ] Frappe services are running
- [ ] Browser cache is cleared
- [ ] You have valid Frappe credentials
- [ ] Network connectivity is stable
- [ ] Browser DevTools are available (F12)

---

## 📝 Testing Procedures

### Test 1: Application Access ✅

**Objective**: Verify the application loads correctly

**Steps**:
1. Open browser and navigate to: `https://prismod.co.ke/app/sigma/`
2. Observe the page loading
3. Check browser console (F12) for errors

**Expected Results**:
- ✅ Page loads without errors
- ✅ Login form is visible
- ✅ No JavaScript errors in console
- ✅ CSS is properly loaded (styled page)

**Troubleshooting**:
- If blank page: Check console for errors
- If 404 error: Verify URL is correct
- If styling is broken: Clear browser cache (Ctrl+Shift+R)

---

### Test 2: Login Functionality ✅

**Objective**: Verify user authentication works

**Steps**:
1. Enter your Frappe user email
2. Enter your password
3. Click "Login" button
4. Observe the redirect

**Expected Results**:
- ✅ Login form accepts input
- ✅ No validation errors for valid credentials
- ✅ Redirects to dashboard after login
- ✅ User information is displayed

**Troubleshooting**:
- If login fails: Check credentials
- If page doesn't redirect: Check browser console
- If session expires: Try logging in again

---

### Test 3: Dashboard Loading ✅

**Objective**: Verify dashboard displays correctly

**Steps**:
1. After successful login, observe dashboard
2. Check for statistics cards
3. Check for recent cases table
4. Check for quick action links

**Expected Results**:
- ✅ Dashboard loads without errors
- ✅ Statistics cards display (Cases, Incidents, Access Events, Guard Shifts)
- ✅ Recent cases table shows data
- ✅ Quick action links are visible
- ✅ All data is properly formatted

**Troubleshooting**:
- If data doesn't load: Check Network tab for API errors
- If styling is broken: Clear cache and refresh
- If numbers are 0: Verify data exists in Frappe

---

### Test 4: Navigation ✅

**Objective**: Verify navigation between modules works

**Steps**:
1. Click on "Cases" in navigation menu
2. Verify page loads
3. Click on "Incidents"
4. Verify page loads
5. Repeat for other modules:
   - Access Control
   - Guard Monitoring
   - Assets
   - Risk Assessment

**Expected Results**:
- ✅ Each module loads without errors
- ✅ Navigation menu highlights current page
- ✅ Page content changes appropriately
- ✅ No console errors

**Modules to Test**:
- Dashboard
- Cases
- Incidents
- Access Control
- Guard Monitoring
- Assets
- Risk Assessment

---

### Test 5: Case Management ✅

**Objective**: Verify case list and details work

**Steps**:
1. Navigate to Cases
2. Observe case list
3. Test search functionality
4. Test filter by status
5. Click on a case to view details
6. Verify all fields display

**Expected Results**:
- ✅ Case list loads with data
- ✅ Search filters cases by title/ID
- ✅ Status filter works
- ✅ Sorting by columns works
- ✅ Pagination works (if >10 cases)
- ✅ Case detail page loads
- ✅ All case fields display correctly

**Test Data**:
- Create test cases if needed
- Use existing cases for testing

---

### Test 6: API Integration ✅

**Objective**: Verify API calls are working

**Steps**:
1. Open browser DevTools (F12)
2. Go to Network tab
3. Navigate to different pages
4. Observe API calls
5. Check response status codes

**Expected Results**:
- ✅ API calls return 200 status
- ✅ Response data is valid JSON
- ✅ No 401 (Unauthorized) errors
- ✅ No 500 (Server) errors
- ✅ Response times are reasonable (<2s)

**API Endpoints to Check**:
- `/api/resource/Case`
- `/api/resource/Incident Report`
- `/api/resource/Access Event`
- `/api/resource/Guard Shift`
- `/api/resource/Asset`
- `/api/resource/Risk Assessment`

---

### Test 7: Responsive Design ✅

**Objective**: Verify application works on different screen sizes

**Steps**:
1. Open DevTools (F12)
2. Click Device Toolbar icon
3. Test different device sizes:
   - Mobile (375x667)
   - Tablet (768x1024)
   - Desktop (1920x1080)
4. Verify layout adapts

**Expected Results**:
- ✅ Mobile layout is readable
- ✅ Navigation is accessible
- ✅ Tables are scrollable
- ✅ Forms are usable
- ✅ No horizontal scrolling needed

---

### Test 8: Error Handling ✅

**Objective**: Verify error messages display correctly

**Steps**:
1. Try invalid login credentials
2. Observe error message
3. Try accessing API with invalid data
4. Observe error handling

**Expected Results**:
- ✅ Error messages are clear
- ✅ User can retry after error
- ✅ No console errors for expected errors
- ✅ Application doesn't crash

---

### Test 9: Performance ✅

**Objective**: Verify application performance

**Steps**:
1. Open DevTools (F12)
2. Go to Performance tab
3. Record page load
4. Analyze metrics

**Expected Results**:
- ✅ Page loads in <2 seconds
- ✅ First Contentful Paint <1 second
- ✅ Largest Contentful Paint <2 seconds
- ✅ Cumulative Layout Shift <0.1

---

### Test 10: Browser Compatibility ✅

**Objective**: Verify application works in different browsers

**Browsers to Test**:
- [ ] Chrome/Edge (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Mobile Chrome
- [ ] Mobile Safari

**Expected Results**:
- ✅ Application loads in all browsers
- ✅ Functionality works consistently
- ✅ Styling is correct
- ✅ No browser-specific errors

---

## 🔍 Browser DevTools Inspection

### Console Tab
```javascript
// Check for errors
// Should see no red error messages
// May see warnings (acceptable)
```

### Network Tab
```
// Check for failed requests
// All requests should have status 200-304
// No 404, 401, or 500 errors
```

### Application Tab
```
// Check cookies
// Should see frappe session cookie
// Check localStorage
// Should see app data if stored
```

### Performance Tab
```
// Check load times
// First Contentful Paint: <1s
// Largest Contentful Paint: <2s
// Cumulative Layout Shift: <0.1
```

---

## 📋 Test Results Template

```markdown
## Test Results - [Date]

### Environment
- Browser: [Chrome/Firefox/Safari]
- OS: [Windows/Mac/Linux]
- URL: https://prismod.co.ke/app/sigma/

### Test Results
- [ ] Test 1: Application Access - ✅/❌
- [ ] Test 2: Login Functionality - ✅/❌
- [ ] Test 3: Dashboard Loading - ✅/❌
- [ ] Test 4: Navigation - ✅/❌
- [ ] Test 5: Case Management - ✅/❌
- [ ] Test 6: API Integration - ✅/❌
- [ ] Test 7: Responsive Design - ✅/❌
- [ ] Test 8: Error Handling - ✅/❌
- [ ] Test 9: Performance - ✅/❌
- [ ] Test 10: Browser Compatibility - ✅/❌

### Issues Found
[List any issues]

### Notes
[Any additional notes]
```

---

## 🐛 Common Issues & Solutions

### Issue: Blank Page
**Solution**:
1. Check browser console (F12)
2. Clear cache (Ctrl+Shift+R)
3. Check network tab for failed requests
4. Verify Frappe is running

### Issue: Login Fails
**Solution**:
1. Verify credentials are correct
2. Check browser console for errors
3. Verify Frappe session is valid
4. Try in incognito mode

### Issue: Data Doesn't Load
**Solution**:
1. Check Network tab for API errors
2. Verify data exists in Frappe
3. Check Frappe permissions
4. Refresh page

### Issue: Styling is Broken
**Solution**:
1. Clear browser cache
2. Hard refresh (Ctrl+Shift+R)
3. Check Network tab for CSS errors
4. Verify CSS file is loaded

### Issue: Slow Performance
**Solution**:
1. Check Network tab for slow requests
2. Verify Frappe server is responsive
3. Check browser performance tab
4. Try in different browser

---

## ✅ Sign-Off

After completing all tests, sign off:

```
Tested By: [Name]
Date: [Date]
Status: ✅ PASSED / ❌ FAILED
Issues: [Number of issues]
Ready for Production: ✅ YES / ❌ NO
```

---

## 📞 Support

For testing issues:
- Email: info@prismod.co.ke
- Documentation: `apps/sigma/sigma/frontend/DEPLOYMENT.md`
- Logs: `logs/web.error.log`

---

**Testing Guide Version**: 1.0.0
**Last Updated**: 2024-10-28

