# Sigma Frontend - Quick Start Guide

## 🚀 Getting Started

### Prerequisites
- Node.js 16+ installed
- npm or yarn package manager
- Frappe bench environment

---

## Installation & Setup

### 1. Navigate to Frontend Directory
```bash
cd apps/sigma/sigma/frontend
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Development Server
```bash
npm run dev
```
Access at: `http://localhost:5173`

### 4. Production Build
```bash
npm run build
```
Output: `../public/dist/`

---

## Project Structure

```
frontend/
├── src/
│   ├── App.vue                 # Main layout component
│   ├── main.js                 # Entry point
│   ├── main.ts                 # TypeScript config
│   ├── assets/
│   │   └── styles/
│   │       └── main.css        # Global styles & colors
│   ├── components/             # Reusable components
│   ├── stores/                 # Pinia state management
│   ├── views/                  # Page components
│   │   ├── Dashboard.vue       # Landing page
│   │   ├── Login.vue           # Login page
│   │   ├── cases/              # Cases module
│   │   ├── incidents/          # Incidents module
│   │   ├── access-control/     # Access control module
│   │   ├── guard-monitoring/   # Guard monitoring module
│   │   ├── assets/             # Assets module
│   │   ├── risk-assessment/    # Risk assessment module
│   │   ├── vehicle-management/ # Vehicle management module
│   │   ├── visitor-management/ # Visitor management module
│   │   ├── helpdesk/           # Helpdesk module
│   │   ├── support/            # Support module
│   │   ├── telephony/          # Telephony module
│   │   ├── projects/           # Projects module
│   │   └── crm/                # CRM module
│   └── router/
│       └── index.js            # Vue Router configuration
├── public/
│   └── dist/                   # Built files (after build)
├── index.html                  # HTML template
├── package.json                # Dependencies
├── vite.config.js              # Vite configuration
└── README.md                   # Project README
```

---

## Available Scripts

### Development
```bash
npm run dev      # Start development server
npm run build    # Build for production
npm run preview  # Preview production build
```

### Linting & Formatting
```bash
npm run lint     # Run ESLint
npm run format   # Format code with Prettier
```

---

## Module Routes

### Security Modules
- `/cases` - Cases management
- `/incidents` - Incidents tracking
- `/access-control` - Access control
- `/guard-monitoring` - Guard monitoring
- `/risk-assessment` - Risk assessment

### Asset & Inventory
- `/assets` - Assets management
- `/vehicle-management` - Vehicle management
- `/visitor-management` - Visitor management

### Support & Operations
- `/helpdesk` - Helpdesk
- `/support` - Support
- `/telephony` - Telephony
- `/projects` - Projects
- `/crm` - CRM

---

## Color Palette

### CSS Variables (in main.css)
```css
--kp-primary: #00337F          /* Deep Blue */
--kp-primary-dark: #002555     /* Darker Blue */
--kp-primary-light: #1A5FA0    /* Light Blue */
--kp-secondary: #00A3E0        /* Electric Blue */
--kp-accent: #FFD100           /* Yellow */
--kp-bg: #F5F7FA               /* Background */
--kp-surface: #FFFFFF          /* Surface */
--kp-text: #1F2937             /* Text */
--kp-muted: #6B7280            /* Muted Text */
--kp-border: #E5E7EB           /* Border */
--kp-hover: #E8F0F8            /* Hover */
```

### Using Colors in Components
```vue
<style scoped>
.my-element {
  background-color: var(--kp-primary);
  color: var(--kp-text);
  border: 1px solid var(--kp-border);
}
</style>
```

---

## Common Tasks

### Add a New Module

1. **Create Component**
   ```bash
   mkdir -p src/views/my-module
   touch src/views/my-module/MyModuleDashboard.vue
   ```

2. **Add Route** (in `src/router/index.js`)
   ```javascript
   import MyModuleDashboard from '../views/my-module/MyModuleDashboard.vue'
   
   {
     path: '/my-module',
     name: 'MyModuleDashboard',
     component: MyModuleDashboard,
     meta: { requiresAuth: true }
   }
   ```

3. **Add Sidebar Link** (in `src/App.vue`)
   ```vue
   <li class="sigma-sidebar-menu-item">
     <router-link
       to="/my-module"
       class="sigma-sidebar-menu-link"
       active-class="active"
       @click="closeSidebarOnMobile"
     >
       <span class="sigma-sidebar-menu-icon">🎯</span>
       <span>My Module</span>
     </router-link>
   </li>
   ```

### Update Colors

Edit `src/assets/styles/main.css`:
```css
:root {
  --kp-primary: #NEW_COLOR;
  /* ... other colors ... */
}
```

### Add Responsive Breakpoint

Edit `src/assets/styles/main.css`:
```css
@media (max-width: 480px) {
  .grid-4 { grid-template-columns: 1fr; }
  .grid-2 { grid-template-columns: 1fr; }
}
```

---

## Deployment

### Build for Production
```bash
npm run build
```

### Deploy to Frappe
1. Built files are in `../public/dist/`
2. Frappe automatically serves them at `/app/sigma/`
3. No additional deployment steps needed

### Access the Application
```
http://your-domain/app/sigma/
```

---

## Troubleshooting

### Port Already in Use
```bash
npm run dev -- --port 3000
```

### Build Errors
```bash
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Module Not Found
- Check route is added in `src/router/index.js`
- Check component path is correct
- Verify component is imported

### Styles Not Applied
- Check CSS variables are defined in `main.css`
- Verify scoped styles syntax
- Clear browser cache

---

## Performance Tips

1. **Lazy Load Routes**
   ```javascript
   const MyModule = () => import('../views/my-module/MyModuleDashboard.vue')
   ```

2. **Optimize Images**
   - Use SVG for icons
   - Compress images before adding

3. **Code Splitting**
   - Vite automatically handles this
   - Monitor bundle size with `npm run build`

---

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

---

## Resources

- [Vue 3 Documentation](https://vuejs.org/)
- [Vue Router Documentation](https://router.vuejs.org/)
- [Vite Documentation](https://vitejs.dev/)
- [Pinia Documentation](https://pinia.vuejs.org/)

---

## Support

For issues or questions:
1. Check the documentation files
2. Review MODULE_REFERENCE.md
3. See IMPLEMENTATION_CHECKLIST.md
4. Refer to FRONTEND_COMPLETION_REPORT.md

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `npm run dev` | Start dev server |
| `npm run build` | Build for production |
| `npm run preview` | Preview build |
| `npm run lint` | Run linter |
| `npm run format` | Format code |

---

**Happy Coding! 🚀**

