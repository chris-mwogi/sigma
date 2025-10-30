# Sigma Frontend - Vue.js Application

A modern, responsive Vue.js 3 frontend for the Sigma Security Management System, integrated with the Frappe backend.

## Features

- **Dashboard**: Real-time overview of security metrics and statistics
- **Case Management**: Create, view, and manage security cases
- **Incident Reports**: Track and manage incident reports
- **Access Control**: Monitor and manage access events and policies
- **Guard Monitoring**: Track guard shifts and activities
- **Asset Management**: Manage security assets and equipment
- **Risk Assessment**: Evaluate and track security risks

## Technology Stack

- **Vue.js 3**: Progressive JavaScript framework
- **Vue Router 4**: Client-side routing
- **Pinia**: State management
- **Axios**: HTTP client for API calls
- **Vite**: Next-generation build tool
- **Frappe REST API**: Backend integration

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable Vue components
│   ├── views/              # Page components
│   │   ├── Dashboard.vue
│   │   ├── Login.vue
│   │   ├── cases/
│   │   ├── incidents/
│   │   ├── access-control/
│   │   ├── guard-monitoring/
│   │   ├── assets/
│   │   └── risk-assessment/
│   ├── stores/             # Pinia state management
│   │   └── auth.js
│   ├── services/           # API services
│   │   └── api.js
│   ├── router/             # Vue Router configuration
│   │   └── index.js
│   ├── assets/             # Static assets
│   │   └── styles/
│   │       └── main.css
│   ├── App.vue             # Root component
│   └── main.js             # Entry point
├── index.html              # HTML template
├── vite.config.js          # Vite configuration
├── package.json            # Dependencies
└── README.md               # This file
```

## Setup Instructions

### Prerequisites

- Node.js 16+ and npm/yarn
- Frappe bench environment
- Sigma app installed on Frappe

### Installation

1. Navigate to the frontend directory:
```bash
cd apps/sigma/sigma/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Build for Production

```bash
npm run build
```

This generates optimized files in `../public/dist/` for deployment.

## Development

### Running the Development Server

```bash
npm run dev
```

The development server includes:
- Hot Module Replacement (HMR)
- API proxy to Frappe backend
- Source maps for debugging

### Code Quality

Run ESLint to check code quality:
```bash
npm run lint
```

## API Integration

The frontend communicates with the Frappe backend via REST API. All API calls are made through the `api` service in `src/services/api.js`.

### Authentication

Authentication is handled through Frappe's session management. The `useAuthStore` in `src/stores/auth.js` manages:
- User login/logout
- Session validation
- User information caching

### API Endpoints Used

#### Cases
- `GET /api/resource/Case` - List all cases
- `GET /api/resource/Case/{id}` - Get case details
- `POST /api/resource/Case` - Create new case

#### Incidents
- `GET /api/resource/Incident Report` - List incidents
- `GET /api/resource/Incident Report/{id}` - Get incident details

#### Access Control
- `GET /api/resource/Access Event` - List access events
- `GET /api/resource/Access Point` - List access points
- `GET /api/resource/Access Policy` - List access policies

#### Guard Monitoring
- `GET /api/resource/Guard Shift` - List guard shifts

#### Assets
- `GET /api/resource/Asset` - List assets
- `GET /api/resource/Asset/{id}` - Get asset details

#### Risk Assessment
- `GET /api/resource/Risk Assessment` - List risk assessments

## Deployment

### Building for Production

1. Build the Vue app:
```bash
npm run build
```

2. The built files are output to `../public/dist/`

3. Update `hooks.py` to include the built assets (already configured)

4. Deploy the Frappe app:
```bash
bench deploy
```

### Asset Bundling

The built assets are automatically included in Frappe through the `hooks.py` configuration:
```python
app_include_js = ["/app/sigma/dist/js/main.js"]
app_include_css = ["/app/sigma/dist/css/main.css"]
```

## Component Documentation

### App.vue
Main application component with:
- Navigation bar with module links
- User menu with logout
- Loading overlay
- Router view for page rendering

### Dashboard.vue
Displays:
- Statistics cards (cases, incidents, access events, guard shifts)
- Recent cases table
- Quick action links

### Case Management
- **CaseList.vue**: List all cases with search, filter, and sort
- **CaseDetail.vue**: View case details
- **CaseForm.vue**: Create new cases

### Incident Management
- **IncidentList.vue**: List all incidents
- **IncidentDetail.vue**: View incident details

### Other Modules
- **AccessControl.vue**: Access control management
- **GuardMonitoring.vue**: Guard shift monitoring
- **AssetList.vue** / **AssetDetail.vue**: Asset management
- **RiskAssessment.vue**: Risk assessment overview

## Styling

Global styles are defined in `src/assets/styles/main.css` with:
- CSS variables for colors and spacing
- Utility classes for common layouts
- Responsive design patterns
- Component-specific scoped styles

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Troubleshooting

### API Calls Failing
- Check that Frappe backend is running
- Verify CSRF token is being sent
- Check browser console for CORS errors

### Build Errors
- Clear `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Clear Vite cache: `rm -rf dist`

### Hot Module Replacement Not Working
- Restart dev server: `npm run dev`
- Check that port 5173 is not in use

## Contributing

When adding new features:
1. Create components in `src/components/`
2. Create views in `src/views/`
3. Add routes to `src/router/index.js`
4. Use Pinia stores for state management
5. Follow existing code style and patterns

## License

MIT License - See LICENSE file for details

## Support

For issues or questions, contact: info@prismod.co.ke

