# KPLC Redesign - Testing Guide

## Pre-Testing Checklist

- [ ] Frontend build completed successfully
- [ ] Cache cleared on Frappe server
- [ ] CSRF token fix is in place
- [ ] API service is configured correctly
- [ ] Browser console is open for debugging

## Testing Environments

### Development
- URL: `https://prismod.co.ke/sigma-frontend`
- Site: `prismod.co.ke`
- Browser: Chrome/Firefox/Safari

### Testing Devices

1. **Desktop (1920x1080)**
   - Full layout with sidebar visible
   - All components should display correctly

2. **Tablet (768x1024)**
   - Responsive layout with adjusted spacing
   - Sidebar should collapse on navigation

3. **Mobile (375x667)**
   - Hamburger menu for sidebar
   - Optimized touch targets
   - Readable text sizes

## Test Cases

### 1. Login Page

**Visual Testing:**
- [ ] Left section displays KPLC branding
- [ ] Lightning bolt icon (⚡) is visible
- [ ] "Kenya Power" text is displayed
- [ ] Features list shows 3 items with icons
- [ ] Right section shows login form
- [ ] Form has email and password fields
- [ ] Sign In button is visible and styled correctly
- [ ] Footer copyright text is present

**Responsive Testing:**
- [ ] Desktop: Split-screen layout (50/50)
- [ ] Tablet: Stacked layout with proper spacing
- [ ] Mobile: Full-width form with optimized padding

**Color Testing:**
- [ ] Left section background: KPLC blue gradient
- [ ] Right section background: Light gray (#f8f9fa)
- [ ] Form heading: KPLC blue (#00337F)
- [ ] Button: KPLC blue with darker hover state
- [ ] Input focus: Blue border with light blue shadow

**Functionality Testing:**
- [ ] Email input accepts valid email format
- [ ] Password input masks characters
- [ ] Sign In button is clickable
- [ ] Form validation works correctly
- [ ] Error messages display properly
- [ ] Loading state shows "Signing in..."

### 2. Header Component

**Visual Testing:**
- [ ] Header background: KPLC blue gradient
- [ ] Lightning bolt icon (⚡) is visible
- [ ] "Kenya Power" text is displayed
- [ ] User name is shown on the right
- [ ] Logout button is visible
- [ ] Header height: 60px

**Responsive Testing:**
- [ ] Desktop: Full header with logo text
- [ ] Tablet: Header with reduced padding
- [ ] Mobile: Logo text hidden, icon only

**Functionality Testing:**
- [ ] Logo click toggles sidebar
- [ ] Logout button works correctly
- [ ] User name displays correctly
- [ ] Header stays fixed at top while scrolling

### 3. Sidebar Component

**Visual Testing:**
- [ ] Background: Light gray (#f8f9fa)
- [ ] Menu items display with icons
- [ ] Active menu item: KPLC blue background and text
- [ ] Hover state: Light blue background
- [ ] Left border accent on active/hover

**Responsive Testing:**
- [ ] Desktop: Sidebar visible (250px width)
- [ ] Tablet: Sidebar collapses on navigation
- [ ] Mobile: Hamburger menu toggles sidebar

**Functionality Testing:**
- [ ] Menu links navigate correctly
- [ ] Active state updates on navigation
- [ ] Sidebar closes on mobile after clicking link
- [ ] Toggle button works correctly

### 4. Dashboard Page

**Visual Testing:**
- [ ] Page heading: "Dashboard" in KPLC blue
- [ ] Subtitle: "Welcome to Kenya Power Security Management System"
- [ ] Stat cards display with correct colors
- [ ] Stat card borders: Color-coded (blue, orange, green)
- [ ] Icons display correctly
- [ ] Values and labels are readable

**Stat Card Colors:**
- [ ] Active Cases: Blue (#00337F)
- [ ] Incidents: Orange (#F39200)
- [ ] Access Events: Green (#00A651)
- [ ] Guard Shifts: Green (#28a745)

**Responsive Testing:**
- [ ] Desktop: 4 columns grid
- [ ] Tablet: 2 columns grid
- [ ] Mobile: 1 column grid

**Table Testing:**
- [ ] Table header: Light blue background (#f0f4f8)
- [ ] Header text: KPLC blue, uppercase
- [ ] Rows display correctly
- [ ] Hover state: Light gray background
- [ ] Status badges: Correct colors

**Functionality Testing:**
- [ ] Dashboard data loads correctly
- [ ] Stat values display correctly
- [ ] Recent cases table populates
- [ ] Quick action links work
- [ ] No console errors

### 5. Color Scheme Testing

**Primary Colors:**
- [ ] KPLC Blue (#00337F): Used in headers, buttons, active states
- [ ] Dark Blue (#002555): Used in hover states, gradients
- [ ] Light Blue (#1a5fa0): Used in backgrounds

**Secondary Colors:**
- [ ] Orange (#F39200): Used in warning/incident indicators
- [ ] Light Orange (#FFB84D): Used in light backgrounds

**Accent Colors:**
- [ ] Green (#00A651): Used in success/access indicators

### 6. Responsive Design Testing

**Breakpoints:**
- [ ] Desktop (>768px): Full layout
- [ ] Tablet (768px): Adjusted layout
- [ ] Mobile (<480px): Optimized layout

**Elements to Test:**
- [ ] Header: Responsive padding and font sizes
- [ ] Sidebar: Collapses correctly
- [ ] Main content: Adjusts to available width
- [ ] Cards: Stack correctly on smaller screens
- [ ] Tables: Responsive or scrollable
- [ ] Forms: Full width on mobile

### 7. Browser Console Testing

**Check for:**
- [ ] No JavaScript errors
- [ ] No console warnings
- [ ] CSRF token is available
- [ ] API calls succeed
- [ ] No 404 errors for assets

**Console Commands:**
```javascript
// Check CSRF token
document.querySelector('meta[name="csrf-token"]').getAttribute('content')

// Check API service
import api from './services/api'
api.get('/api/resource/User')
```

### 8. Performance Testing

**Metrics to Check:**
- [ ] Page load time < 3 seconds
- [ ] CSS file size: ~25 kB
- [ ] JS file size: ~175 kB
- [ ] No layout shifts
- [ ] Smooth animations

### 9. Accessibility Testing

**Keyboard Navigation:**
- [ ] Tab through form fields
- [ ] Enter submits form
- [ ] Escape closes modals
- [ ] Focus visible on all interactive elements

**Screen Reader Testing:**
- [ ] Page structure is logical
- [ ] Form labels are associated
- [ ] Buttons have descriptive text
- [ ] Images have alt text

### 10. Cross-Browser Testing

**Browsers to Test:**
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Chrome Mobile
- [ ] Safari Mobile

## Bug Reporting Template

**Title:** [Component] Issue description

**Environment:**
- Browser: 
- OS: 
- Screen size: 
- URL: 

**Steps to Reproduce:**
1. 
2. 
3. 

**Expected Result:**

**Actual Result:**

**Screenshots/Videos:**

**Console Errors:**

## Sign-Off

- [ ] All test cases passed
- [ ] No critical bugs found
- [ ] Responsive design verified
- [ ] Performance acceptable
- [ ] Ready for production deployment

**Tested by:** _______________
**Date:** _______________
**Notes:** _______________

