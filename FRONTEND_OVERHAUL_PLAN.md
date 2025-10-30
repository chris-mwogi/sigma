# Sigma Frontend Comprehensive Overhaul Plan

## Executive Summary

The sigma app's Vue frontend has critical structural issues that are causing broken links and potentially contributing to the desk interface errors. This document outlines a comprehensive overhaul to restructure the frontend following the proven hmis_setup pattern.

## Current Issues Identified

### 1. Router Configuration Mismatch
- **Problem**: Router configured with base path `/app/sigma/` but page served at `/sigma-frontend`
- **Impact**: All navigation links are broken, routes don't resolve correctly
- **File**: `apps/sigma/sigma/frontend/src/router/index.js` line 143

### 2. Incorrect Directory Structure
- **Problem**: Frontend in separate `sigma/frontend/` directory instead of `sigma/public/js/`
- **Impact**: Build process doesn't align with Frappe conventions, asset paths are incorrect
- **Comparison**:
  ```
  ❌ Current: apps/sigma/sigma/frontend/src/
  ✅ Target:  apps/sigma/sigma/public/js/src/
  ```

### 3. Missing UI Framework
- **Problem**: No Element Plus or modern UI library
- **Impact**: Inconsistent UI, no pre-built responsive components
- **Solution**: Add Element Plus like hmis_setup

### 4. Build Configuration Issues
- **Problem**: Vite builds to `../public/dist` with incorrect asset paths
- **Impact**: Assets not found, CSS/JS files 404
- **File**: `apps/sigma/sigma/frontend/vite.config.js`

### 5. Non-Responsive Sidebar
- **Problem**: Sidebar doesn't collapse properly on mobile, no persistent state
- **Impact**: Poor mobile experience, unusable on small screens
- **File**: `apps/sigma/sigma/frontend/src/App.vue`

## Proposed Solution: Match HMIS Setup Pattern

### Phase 1: Directory Restructuring

#### Step 1.1: Move Frontend Source
```bash
# Move from sigma/frontend/src to sigma/public/js/src
mv apps/sigma/sigma/frontend/src apps/sigma/sigma/public/js/src
mv apps/sigma/sigma/frontend/package.json apps/sigma/sigma/public/js/
mv apps/sigma/sigma/frontend/vite.config.js apps/sigma/sigma/public/js/
mv apps/sigma/sigma/frontend/index.html apps/sigma/sigma/public/js/
```

#### Step 1.2: Update Build Output
- Change vite output from `../public/dist` to `../dist`
- Update asset paths to use `/assets/sigma/dist/`

### Phase 2: Add Element Plus

#### Step 2.1: Update package.json
Add dependencies:
```json
{
  "dependencies": {
    "vue": "^3.3.4",
    "vue-router": "^4.2.4",
    "pinia": "^2.1.7",
    "axios": "^1.5.0",
    "element-plus": "^2.4.0"
  }
}
```

#### Step 2.2: Configure Element Plus
Update `main.js` to import and use Element Plus globally

### Phase 3: Fix Router Configuration

#### Step 3.1: Update Router Base Path
Change from `/app/sigma/` to `/sigma-frontend/`

#### Step 3.2: Fix Navigation Guards
Ensure auth checks work with Frappe session

### Phase 4: Implement Responsive Design

#### Step 4.1: Update App.vue
- Add collapsible sidebar with persistent state
- Implement mobile overlay
- Add responsive breakpoints
- Use Element Plus components (el-header, el-aside, el-main, el-menu)

#### Step 4.2: Modern Theme
- Implement color scheme matching KPLC branding
- Add smooth transitions
- Improve typography

### Phase 5: Update WWW Handler

#### Step 5.1: Update sigma-frontend.html
- Fix asset paths to point to `/assets/sigma/dist/`
- Remove inline styles (moved to Vue components)
- Add Element Plus CSS

#### Step 5.2: Update sigma-frontend.py
- Ensure proper context passing
- Add user authentication check

## Detailed File Changes

### 1. apps/sigma/sigma/public/js/package.json (NEW LOCATION)
```json
{
  "name": "sigma-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.3.4",
    "vue-router": "^4.2.4",
    "pinia": "^2.1.7",
    "axios": "^1.5.0",
    "element-plus": "^2.4.0",
    "@element-plus/icons-vue": "^2.1.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^4.3.4",
    "vite": "^4.4.9"
  }
}
```

### 2. apps/sigma/sigma/public/js/vite.config.js (NEW LOCATION)
```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    outDir: '../dist',
    target: 'es2017',
    rollupOptions: {
      input: path.resolve(__dirname, 'src/main.js'),
      output: {
        format: 'iife',
        entryFileNames: 'sigma-app.js',
        chunkFileNames: 'sigma-app-[name].js',
        assetFileNames: (assetInfo) => {
          if (assetInfo.name.endsWith('.css')) {
            return 'sigma-app.css'
          }
          return '[name].[ext]'
        },
        name: 'SigmaApp',
      },
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

### 3. apps/sigma/sigma/public/js/src/main.js (UPDATED)
```javascript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'

const app = createApp(App)
const pinia = createPinia()

// Register Element Plus
app.use(ElementPlus)

// Register all Element Plus icons
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.use(component.name, component)
}

app.use(pinia)
app.use(router)

app.mount('#app')
```

### 4. apps/sigma/sigma/public/js/src/router/index.js (UPDATED)
```javascript
import { createRouter, createWebHashHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

// ... imports ...

const router = createRouter({
  history: createWebHashHistory(),  // Use hash mode for Frappe compatibility
  routes
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Check if route requires auth
  if (to.meta.requiresAuth !== false) {
    // Check if user is authenticated
    if (!authStore.isAuthenticated) {
      await authStore.checkAuth()
    }
    
    if (!authStore.isAuthenticated) {
      next('/login')
      return
    }
  }
  
  next()
})

export default router
```

### 5. apps/sigma/sigma/www/sigma-frontend.html (UPDATED)
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="{{ csrf_token }}">
    <title>Sigma - Security Management System</title>
    <link rel="icon" href="/assets/sigma/public/images/icon.svg">
    <link rel="stylesheet" href="/assets/sigma/dist/sigma-app.css">
</head>
<body>
    <div id="app"></div>
    <script type="module" src="/assets/sigma/dist/sigma-app.js"></script>
</body>
</html>
```

## Implementation Steps

### Step 1: Backup Current Frontend
```bash
cd /Users/mwogi/frappe-bench/apps/sigma
cp -r sigma/frontend sigma/frontend.backup
```

### Step 2: Create New Directory Structure
```bash
mkdir -p sigma/public/js/src
```

### Step 3: Move Files
```bash
# Move source files
mv sigma/frontend/src/* sigma/public/js/src/
# Move config files
mv sigma/frontend/package.json sigma/public/js/
mv sigma/frontend/vite.config.js sigma/public/js/
mv sigma/frontend/index.html sigma/public/js/
```

### Step 4: Update Configuration Files
- Update vite.config.js
- Update package.json
- Update main.js
- Update router/index.js
- Update App.vue

### Step 5: Install Dependencies
```bash
cd sigma/public/js
npm install
```

### Step 6: Build Frontend
```bash
npm run build
```

### Step 7: Update WWW Files
- Update sigma-frontend.html
- Update sigma-frontend.py

### Step 8: Test
```bash
cd /Users/mwogi/frappe-bench
bench --site sigma.localhost clear-cache
bench build --app sigma
```

## Expected Outcomes

1. ✅ Frontend accessible at `/sigma-frontend`
2. ✅ All routes work correctly with hash-based routing
3. ✅ Responsive sidebar that collapses on mobile
4. ✅ Modern UI with Element Plus components
5. ✅ Proper authentication flow
6. ✅ No 404 errors for assets
7. ✅ Mobile-responsive design
8. ✅ Persistent sidebar state

## Testing Checklist

- [ ] Navigate to http://sigma.localhost:8000/sigma-frontend
- [ ] Verify login page loads
- [ ] Test authentication
- [ ] Navigate to all routes (Dashboard, Cases, Incidents, etc.)
- [ ] Test sidebar collapse/expand
- [ ] Test on mobile viewport (< 768px)
- [ ] Verify no console errors
- [ ] Check network tab for 404s
- [ ] Test logout functionality
- [ ] Verify CSRF token handling

## Rollback Plan

If issues occur:
```bash
cd /Users/mwogi/frappe-bench/apps/sigma
rm -rf sigma/public/js
mv sigma/frontend.backup sigma/frontend
bench build --app sigma
bench --site sigma.localhost clear-cache
```

## Next Steps After Overhaul

1. Update all view components to use Element Plus
2. Implement proper error handling
3. Add loading states
4. Improve API error messages
5. Add user feedback (toasts, notifications)
6. Implement proper form validation
7. Add data tables with sorting/filtering
8. Implement search functionality

## Timeline Estimate

- Phase 1 (Restructuring): 30 minutes
- Phase 2 (Element Plus): 20 minutes
- Phase 3 (Router Fix): 15 minutes
- Phase 4 (Responsive Design): 45 minutes
- Phase 5 (WWW Handler): 15 minutes
- Testing & Debugging: 30 minutes

**Total**: ~2.5 hours

## Risk Assessment

**Low Risk**:
- Directory restructuring (can be rolled back)
- Adding Element Plus (additive change)

**Medium Risk**:
- Router configuration changes (may need debugging)
- Build configuration updates (may need iteration)

**High Risk**:
- None (all changes are reversible)

## Success Criteria

1. Frontend loads without errors
2. All navigation links work
3. Sidebar is responsive
4. No 404 errors in console
5. Authentication works correctly
6. Mobile experience is smooth
7. Desk interface errors are resolved

