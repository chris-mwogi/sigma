# Sigma App Technical Restructuring Guide

## Architecture Overview

### Before Restructuring
```
Frappe Desk (/app)
├── Vue.js Bundle (included via app_include_js)
├── Dashboard Pages
├── Portal Menu Items
└── Workspace Sidebar (broken by Vue.js interference)
```

### After Restructuring
```
Frappe Desk (/app)
├── LinksWidget Patch (fixes sidebar)
└── Workspace Sidebar (working correctly)

Sigma Frontend (/sigma-frontend)
├── Vue.js SPA
├── Header with Logo
├── Collapsible Sidebar
└── Mobile Responsive Design
```

## Key Changes

### 1. hooks.py Configuration

#### Before
```python
app_include_js = [
    "/assets/sigma/dist/js/index.js",  # Vue.js bundle
    "/assets/sigma/js/patches/links_widget_fix.js"
]
app_include_css = [
    "/assets/sigma/dist/css/index.css"  # Vue.js styles
]
page_js = {
    "sigma-home": "sigma/public/js/pages/sigma_home.js"
}
portal_menu_items = [...]
```

#### After
```python
app_include_js = [
    "/assets/sigma/js/patches/links_widget_fix.js"  # Only patch
]
# Removed: app_include_css, page_js, portal_menu_items

website_route_rules = [
    {"from_route": "/sigma-frontend", "to_route": "sigma-frontend"}
]
```

### 2. Frontend Route Handler

#### New File: sigma-frontend.py
```python
import frappe

def get_context(context):
    context.user = frappe.session.user
    context.user_full_name = frappe.db.get_value("User", frappe.session.user, "full_name")
    context.user_roles = frappe.get_roles(frappe.session.user)
    context.page_title = "Sigma - Security Management System"
    context.no_cache = 1
    return context
```

#### New File: sigma-frontend.html
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sigma - Security Management System</title>
    <style>
        /* Header, Sidebar, and Responsive CSS */
    </style>
</head>
<body>
    <div id="app"></div>
    <script type="module" src="/assets/sigma/dist/js/index.js"></script>
    <link rel="stylesheet" href="/assets/sigma/dist/css/index.css">
</body>
</html>
```

### 3. Vue.js App Component

#### Updated App.vue Structure
```vue
<template>
  <div id="app" class="sigma-app">
    <!-- Header -->
    <header class="sigma-header">
      <button class="sigma-toggle-btn" @click="toggleSidebar">☰</button>
      <div class="sigma-header-logo" @click="toggleSidebar">Σ Sigma</div>
      <div class="sigma-header-spacer"></div>
      <div class="sigma-header-user">
        <span>{{ currentUser }}</span>
        <button @click="logout">Logout</button>
      </div>
    </header>

    <!-- Sidebar -->
    <aside class="sigma-sidebar" :class="{ collapsed: sidebarCollapsed }">
      <ul class="sigma-sidebar-menu">
        <li v-for="item in menuItems" :key="item.path">
          <router-link :to="item.path" @click="closeSidebarOnMobile">
            <span class="icon">{{ item.icon }}</span>
            <span>{{ item.label }}</span>
          </router-link>
        </li>
      </ul>
    </aside>

    <!-- Main Content -->
    <main class="sigma-main" :class="{ expanded: sidebarCollapsed }">
      <router-view />
    </main>
  </div>
</template>

<script>
export default {
  setup() {
    const sidebarCollapsed = ref(false)
    
    const toggleSidebar = () => {
      sidebarCollapsed.value = !sidebarCollapsed.value
    }
    
    const closeSidebarOnMobile = () => {
      if (window.innerWidth <= 768) {
        sidebarCollapsed.value = true
      }
    }
    
    return { sidebarCollapsed, toggleSidebar, closeSidebarOnMobile }
  }
}
</script>

<style scoped>
.sigma-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: linear-gradient(135deg, #0084ff 0%, #0066cc 100%);
  display: flex;
  align-items: center;
  z-index: 1000;
}

.sigma-sidebar {
  position: fixed;
  left: 0;
  top: 60px;
  width: 250px;
  height: calc(100vh - 60px);
  background: #2c3e50;
  transition: transform 0.3s ease;
  z-index: 999;
}

.sigma-sidebar.collapsed {
  transform: translateX(-100%);
}

.sigma-main {
  margin-left: 250px;
  margin-top: 60px;
  transition: margin-left 0.3s ease;
}

.sigma-main.expanded {
  margin-left: 0;
}

@media (max-width: 768px) {
  .sigma-sidebar {
    width: 100%;
  }
  .sigma-main {
    margin-left: 0;
  }
}
</style>
```

### 4. LinksWidget Patch

#### Purpose
Fixes the `TypeError: can't access property "toLowerCase", name2 is null` error that occurs when Frappe's LinksWidget encounters Card Break items with null `link_type`.

#### Implementation
```javascript
(function() {
  if (typeof frappe === 'undefined') {
    setTimeout(arguments.callee, 100);
    return;
  }

  // Patch the LinksWidget to skip Card Break items
  const originalSetBody = frappe.widget?.LinksWidget?.prototype?.set_body;
  
  if (originalSetBody) {
    frappe.widget.LinksWidget.prototype.set_body = function() {
      // Filter out Card Break items before processing
      if (this.links && Array.isArray(this.links)) {
        this.links = this.links.filter(item => item.type !== 'Card Break');
      }
      
      // Call original set_body
      return originalSetBody.call(this);
    };
  }

  console.log('[Sigma Patch] LinksWidget fix applied');
})();
```

## CSS Responsive Design

### Breakpoints
```css
/* Desktop (> 768px) */
.sigma-sidebar { width: 250px; }
.sigma-main { margin-left: 250px; }

/* Tablet (768px) */
@media (max-width: 768px) {
  .sigma-sidebar { width: 100%; }
  .sigma-main { margin-left: 0; }
}

/* Mobile (< 480px) */
@media (max-width: 480px) {
  .sigma-header { padding: 0 10px; }
  .logo-text { display: none; }
  .user-name { display: none; }
}
```

## Asset Paths

### Frontend Assets
```
/assets/sigma/dist/js/index.js       (Vue.js bundle)
/assets/sigma/dist/css/index.css     (Vue.js styles)
/assets/sigma/js/patches/links_widget_fix.js  (Patch)
```

### Served From
```
apps/sigma/sigma/public/dist/js/index.js
apps/sigma/sigma/public/dist/css/index.css
apps/sigma/sigma/public/js/patches/links_widget_fix.js
```

## Deployment Process

### 1. Build Frontend
```bash
cd apps/sigma/sigma/frontend
npm run build
# Output: apps/sigma/sigma/public/dist/
```

### 2. Link Assets
```bash
bench build --app sigma
# Links assets to public directory
```

### 3. Clear Cache
```bash
bench --site prismod.co.ke clear-cache
```

### 4. Restart Services
```bash
bench restart
# Restarts gunicorn and other services
```

## Troubleshooting

### Frontend Not Loading
1. Check if Vue.js bundle is built: `ls apps/sigma/sigma/public/dist/js/index.js`
2. Verify asset paths in `sigma-frontend.html`
3. Check browser console for 404 errors
4. Run `bench build --app sigma` to link assets

### Sidebar Not Collapsing
1. Check if `sidebarCollapsed` state is defined in App.vue
2. Verify CSS classes are applied: `.sigma-sidebar.collapsed`
3. Check browser console for JavaScript errors
4. Verify `toggleSidebar()` function is called on click

### Mobile Not Responsive
1. Check viewport meta tag: `<meta name="viewport" content="width=device-width, initial-scale=1.0">`
2. Verify CSS media queries are correct
3. Test with browser dev tools device emulation
4. Check if `closeSidebarOnMobile()` is called on navigation

### Frappe Desk Broken
1. Check if Vue.js bundle is removed from `app_include_js`
2. Verify only LinksWidget patch is included
3. Check browser console for errors
4. Run `bench clear-cache` and restart

## Performance Considerations

### Frontend
- Vue.js bundle is only loaded at `/sigma-frontend`
- Frappe desk is not affected by Vue.js
- Sidebar toggle uses CSS transforms (GPU accelerated)
- Mobile sidebar uses full-width overlay (no layout shift)

### Backend
- Frappe desk loads faster without Vue.js bundle
- LinksWidget patch is minimal (< 2KB)
- No additional database queries

## Security Considerations

### Frontend
- User authentication via Frappe session
- User roles passed to frontend context
- API calls use Frappe's CSRF protection
- Frontend runs in same domain as backend

### Backend
- Frappe desk remains fully functional
- All Frappe security features intact
- LinksWidget patch doesn't modify data
- No new security vulnerabilities introduced

---

**Last Updated**: 2025-10-28
**Version**: 1.0
**Status**: Complete

