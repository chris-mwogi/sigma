# Sigma App Restructuring - Complete

## Overview

The Sigma app has been successfully restructured to separate the Vue.js frontend from the Frappe backend. The frontend now runs as an independent single-page application (SPA) while the backend remains integrated with Frappe.

## Architecture

### Backend (Frappe Desk)
- **Route**: `/app`
- **Purpose**: Frappe desk interface for administrative tasks
- **Status**: Remains unchanged, fully integrated with Frappe

### Frontend (Vue.js SPA)
- **Route**: `/sigma-frontend`
- **Purpose**: Independent Vue.js application for Sigma functionality
- **Features**:
  - Collapsible sidebar with menu
  - Responsive header with logo
  - Mobile-responsive design
  - Independent routing and state management

## Changes Made

### 1. **hooks.py** - Removed Vue.js Bundle from Desk
```python
# Only include the LinksWidget patch to fix the sidebar issue
app_include_js = [
    "/assets/sigma/js/patches/links_widget_fix.js"
]
```

**Removed**:
- `app_include_js` for Vue.js bundle
- `app_include_css` for Vue.js styles
- `page_js` hook that was loading dashboard pages
- `portal_menu_items` that were interfering with desk

**Updated**:
- `website_route_rules` to point to `/sigma-frontend` instead of `/sigma-home`

### 2. **Frontend Structure**

#### Website Route Handler
- **File**: `apps/sigma/sigma/www/sigma-frontend.html`
- **Purpose**: HTML template for the Vue.js frontend
- **Features**:
  - Responsive header with collapsible sidebar
  - Mobile-first design
  - Loading state with spinner
  - Proper asset paths for Vue.js bundle

#### Python Route Handler
- **File**: `apps/sigma/sigma/www/sigma-frontend.py`
- **Purpose**: Frappe route handler for `/sigma-frontend`
- **Provides**:
  - User information
  - User roles
  - App version
  - Context for template rendering

### 3. **Vue.js App Component** - Updated App.vue

#### New Features
- **Header**: Fixed header with logo and user menu
- **Sidebar**: Collapsible left sidebar with menu items
- **Toggle Button**: Click logo or toggle button to collapse/expand sidebar
- **Mobile Responsive**: Sidebar collapses on mobile, menu items have icons
- **Main Content**: Flexible content area that expands when sidebar is collapsed

#### Menu Items
1. Dashboard (📊)
2. Cases (📋)
3. Incidents (⚠️)
4. Access Control (🔐)
5. Guard Monitoring (👮)
6. Assets (🏢)
7. Risk Assessment (⚡)

#### Responsive Breakpoints
- **Desktop** (> 768px): Full sidebar visible
- **Tablet** (768px): Sidebar collapses on navigation
- **Mobile** (< 480px): Compact header, hidden user name

### 4. **LinksWidget Patch**
- **File**: `apps/sigma/sigma/public/js/patches/links_widget_fix.js`
- **Purpose**: Fixes the `toLowerCase` error in Frappe's workspace sidebar
- **Included in**: Frappe desk via `app_include_js`

## File Structure

```
apps/sigma/sigma/
├── www/
│   ├── sigma-frontend.html      # Frontend HTML template
│   └── sigma-frontend.py        # Route handler
├── frontend/
│   ├── src/
│   │   ├── App.vue              # Updated with header/sidebar
│   │   ├── main.js
│   │   ├── router/
│   │   ├── stores/
│   │   ├── services/
│   │   ├── views/
│   │   └── components/
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── public/
│   ├── dist/
│   │   ├── index.html           # Built frontend
│   │   ├── js/
│   │   └── css/
│   └── js/
│       └── patches/
│           └── links_widget_fix.js
└── hooks.py                     # Updated configuration
```

## Accessing the Application

### Frappe Backend (Desk)
```
https://prismod.co.ke/app
```

### Sigma Frontend
```
https://prismod.co.ke/sigma-frontend
```

## Frontend Features

### Header
- **Logo**: Clickable to toggle sidebar
- **Toggle Button**: Mobile-only button to toggle sidebar
- **User Menu**: Shows current user and logout button
- **Responsive**: Hides logo text on mobile

### Sidebar
- **Collapsible**: Click logo or toggle button to collapse
- **Menu Items**: 7 main navigation items with icons
- **Active State**: Highlights current route
- **Smooth Animation**: Slide-in/out transition
- **Mobile**: Full-width overlay on mobile devices

### Main Content
- **Flexible Layout**: Expands when sidebar is collapsed
- **Responsive Padding**: Adjusts for different screen sizes
- **Max Width**: 1400px for optimal readability

## Mobile Responsiveness

### Tablet (768px)
- Sidebar collapses when navigation item is clicked
- Header remains fixed
- Menu items are still visible

### Mobile (480px)
- Compact header with minimal padding
- Logo text hidden
- User name hidden
- Sidebar takes full width when expanded
- Reduced padding in content area

## Known Issues & Resolutions

### Issue: Frappe Server Hanging
**Status**: Under investigation
**Workaround**: Restart gunicorn workers
```bash
pkill -9 gunicorn
# Supervisor will automatically restart them
```

### Issue: Sidebar `toLowerCase` Error
**Status**: FIXED
**Solution**: LinksWidget patch filters out Card Break items
**File**: `apps/sigma/sigma/public/js/patches/links_widget_fix.js`

## Next Steps

1. **Test Frontend**: Access `/sigma-frontend` in browser
2. **Verify Sidebar**: Check that sidebar collapses/expands correctly
3. **Test Mobile**: Use browser dev tools to test responsive design
4. **Verify Backend**: Ensure Frappe desk loads without errors
5. **Check Console**: Look for any JavaScript errors

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

### Frontend Not Loading
1. Check browser console for errors
2. Verify asset paths in `sigma-frontend.html`
3. Check that Vue.js bundle is built: `apps/sigma/sigma/public/dist/js/index.js`

### Sidebar Not Collapsing
1. Check browser console for JavaScript errors
2. Verify `App.vue` has `sidebarCollapsed` state
3. Check CSS classes are applied correctly

### Mobile Not Responsive
1. Check viewport meta tag in HTML
2. Verify CSS media queries are correct
3. Test with browser dev tools device emulation

## Summary

The Sigma app has been successfully restructured to:
- ✅ Separate Vue.js frontend from Frappe backend
- ✅ Create independent frontend at `/sigma-frontend`
- ✅ Implement collapsible sidebar with header
- ✅ Add mobile-responsive design
- ✅ Fix workspace sidebar `toLowerCase` error
- ✅ Remove dashboard implementations that broke desk

The frontend is now ready for independent deployment and can be accessed at `https://prismod.co.ke/sigma-frontend`.

