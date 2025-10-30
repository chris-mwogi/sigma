# Sigma Frontend - Quick Start Guide

Get the Sigma Vue.js frontend up and running in 5 minutes.

## Prerequisites

- Node.js 16+ installed
- npm or yarn package manager
- Frappe bench environment
- Sigma app installed on Frappe

## Installation (5 minutes)

### 1. Navigate to Frontend Directory
```bash
cd apps/sigma/sigma/frontend
```

### 2. Install Dependencies
```bash
npm install
```
This installs all required packages (Vue, Router, Pinia, Axios, etc.)

### 3. Start Development Server
```bash
npm run dev
```

Output:
```
  VITE v4.4.9  ready in 123 ms

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

### 4. Open in Browser
Navigate to: `http://localhost:5173/`

You should see the Sigma login page.

## First Steps

### Login
1. Enter your Frappe user email
2. Enter your password
3. Click "Login"

### Explore Dashboard
After login, you'll see:
- Statistics cards (Cases, Incidents, Access Events, Guard Shifts)
- Recent cases table
- Quick action links

### Navigate Modules
Use the top navigation bar to access:
- **Dashboard** - Overview and statistics
- **Cases** - Case management
- **Incidents** - Incident reports
- **Access Control** - Access management
- **Guard Monitoring** - Guard shifts
- **Assets** - Asset management
- **Risk Assessment** - Risk analysis

## Common Tasks

### Create a New Case
1. Click "Cases" in navigation
2. Click "+ New Case" button
3. Fill in the form:
   - Title (required)
   - Description
   - Priority
   - Status
4. Click "Create Case"

### View Case Details
1. Click "Cases" in navigation
2. Click "View" button on any case
3. See full case information

### Search and Filter
1. Use search box to find items
2. Use filter dropdowns to narrow results
3. Click column headers to sort

### Refresh Data
Click the "🔄 Refresh" button to reload data from server.

## Development

### File Structure
```
frontend/
├── src/
│   ├── views/          # Page components
│   ├── components/     # Reusable components
│   ├── stores/         # State management
│   ├── services/       # API services
│   ├── router/         # Routing
│   ├── assets/         # Styles and images
│   ├── App.vue         # Root component
│   └── main.js         # Entry point
├── index.html          # HTML template
├── vite.config.js      # Build config
└── package.json        # Dependencies
```

### Edit a Component
1. Open a `.vue` file in `src/views/` or `src/components/`
2. Make changes
3. Save file
4. Browser automatically reloads (Hot Module Replacement)

### Add a New Page
1. Create new file in `src/views/MyPage.vue`
2. Add route in `src/router/index.js`
3. Add navigation link in `src/App.vue`

Example route:
```javascript
{
  path: '/my-page',
  name: 'MyPage',
  component: MyPage,
  meta: { requiresAuth: true }
}
```

### Call an API
Use the `api` service:

```javascript
import api from '@/services/api'

// GET request
const response = await api.get('/api/resource/Case')

// POST request
const response = await api.post('/api/resource/Case', {
  title: 'New Case',
  status: 'Open'
})
```

### Use State Management
Use Pinia stores:

```javascript
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
console.log(authStore.user)
console.log(authStore.isAuthenticated)
```

## Debugging

### Browser DevTools
1. Press `F12` to open DevTools
2. **Console** tab - See errors and logs
3. **Network** tab - See API calls
4. **Application** tab - See cookies and storage

### Vue DevTools
Install Vue DevTools browser extension:
- Chrome: https://chrome.google.com/webstore
- Firefox: https://addons.mozilla.org

Then inspect Vue components in DevTools.

### Common Issues

**Blank page?**
- Check browser console for errors
- Verify Frappe backend is running
- Try hard refresh: Ctrl+Shift+R

**API calls failing?**
- Check Network tab for request/response
- Verify you're logged in
- Check Frappe backend logs

**Styles not loading?**
- Clear browser cache
- Restart dev server: `npm run dev`
- Check that `main.css` is imported

## Build for Production

```bash
npm run build
```

Creates optimized files in `../public/dist/`

Then deploy to Frappe:
```bash
cd /path/to/frappe-bench
bench deploy
```

## Useful Commands

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Check code quality
npm run lint

# Install new package
npm install package-name

# Update all packages
npm update
```

## Project Structure Explained

### `src/views/`
Full-page components for each feature:
- Dashboard.vue
- cases/CaseList.vue, CaseDetail.vue, CaseForm.vue
- incidents/IncidentList.vue, IncidentDetail.vue
- access-control/AccessControl.vue
- guard-monitoring/GuardMonitoring.vue
- assets/AssetList.vue, AssetDetail.vue
- risk-assessment/RiskAssessment.vue

### `src/components/`
Reusable components used across pages (to be created as needed)

### `src/stores/`
Pinia state management:
- auth.js - User authentication state

### `src/services/`
API and utility services:
- api.js - Axios instance with Frappe integration

### `src/router/`
Vue Router configuration:
- index.js - All routes and navigation guards

### `src/assets/`
Static assets:
- styles/main.css - Global styles

## Next Steps

1. **Explore the code** - Read through existing components
2. **Make changes** - Try editing a component
3. **Add features** - Create new pages or components
4. **Deploy** - Build and deploy to production
5. **Learn more** - Read detailed documentation:
   - README.md - Full documentation
   - API_DOCUMENTATION.md - API endpoints
   - COMPONENT_GUIDE.md - Component development
   - DEPLOYMENT.md - Production deployment

## Getting Help

- **Vue Documentation**: https://vuejs.org
- **Frappe Documentation**: https://frappeframework.com
- **Project Issues**: Check browser console and network tab
- **Support**: info@prismod.co.ke

## Tips

✅ Use Vue DevTools for debugging
✅ Check Network tab for API issues
✅ Use browser console to test code
✅ Read existing components for patterns
✅ Keep components small and focused
✅ Use TypeScript for better IDE support (optional)
✅ Write tests for critical features

## Troubleshooting

### Port 5173 already in use
```bash
npm run dev -- --port 5174
```

### Module not found errors
```bash
rm -rf node_modules
npm install
```

### Vite cache issues
```bash
rm -rf dist
npm run dev
```

### API CORS errors
- Ensure Frappe backend is running
- Check that you're on the same domain
- Verify CSRF token is being sent

## Happy Coding! 🚀

You're now ready to develop with Sigma frontend. Start by exploring the existing code and making small changes to understand how everything works.

