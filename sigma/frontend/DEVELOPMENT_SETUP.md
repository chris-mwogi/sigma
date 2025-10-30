# Sigma Frontend - Development Environment Setup

Complete guide for setting up a development environment for the Sigma frontend.

## System Requirements

- **OS**: Linux, macOS, or Windows (with WSL2)
- **Node.js**: 16.x or higher
- **npm**: 7.x or higher (comes with Node.js)
- **Git**: 2.x or higher
- **RAM**: 4GB minimum (8GB recommended)
- **Disk Space**: 2GB for node_modules

## Installation Steps

### 1. Install Node.js

#### macOS (using Homebrew)
```bash
brew install node
```

#### Ubuntu/Debian
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### Windows
Download from: https://nodejs.org/

#### Verify Installation
```bash
node --version
npm --version
```

### 2. Clone/Navigate to Project

```bash
cd /path/to/frappe-bench/apps/sigma/sigma/frontend
```

### 3. Install Dependencies

```bash
npm install
```

This installs all packages listed in `package.json`:
- Vue 3
- Vue Router
- Pinia
- Axios
- Vite
- ESLint

### 4. Verify Installation

```bash
npm run dev
```

You should see:
```
  VITE v4.4.9  ready in 123 ms

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

## IDE Setup

### Visual Studio Code (Recommended)

#### Install Extensions
1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Install:
   - **Volar** - Vue 3 support
   - **ESLint** - Code quality
   - **Prettier** - Code formatting
   - **Thunder Client** - API testing

#### VS Code Settings

Create `.vscode/settings.json`:
```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "[vue]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "eslint.validate": [
    "javascript",
    "javascriptreact",
    "vue"
  ],
  "vetur.validation.template": true
}
```

### WebStorm / IntelliJ IDEA

1. Open project
2. Go to Settings > Languages & Frameworks > JavaScript > Vue.js
3. Enable Vue.js support
4. Install Vue.js plugin if prompted

### Sublime Text

Install packages:
- Vue Syntax Highlight
- Babel
- ESLint

## Browser Setup

### Chrome/Edge

1. Install **Vue DevTools** extension
   - Chrome: https://chrome.google.com/webstore
   - Edge: https://microsoftedge.microsoft.com/addons

2. Open DevTools (F12)
3. Go to Vue tab to inspect components

### Firefox

1. Install **Vue DevTools** extension
   - Firefox: https://addons.mozilla.org

## Development Workflow

### Start Development Server

```bash
npm run dev
```

Features:
- Hot Module Replacement (HMR)
- Automatic browser refresh
- Source maps for debugging
- API proxy to Frappe backend

### Edit Files

1. Open file in editor
2. Make changes
3. Save file
4. Browser automatically reloads

### Debug in Browser

1. Press F12 to open DevTools
2. **Console** tab - View errors and logs
3. **Sources** tab - Set breakpoints
4. **Vue** tab - Inspect Vue components
5. **Network** tab - Monitor API calls

### Run Linter

```bash
npm run lint
```

Checks code quality and fixes issues.

## Git Workflow

### Clone Repository

```bash
git clone https://github.com/chris-mwogi/frappe-bench.git
cd frappe-bench
```

### Create Feature Branch

```bash
git checkout -b feature/my-feature
```

### Make Changes

```bash
# Edit files
# Test changes
# Commit changes
git add .
git commit -m "feat: Add new feature"
```

### Push Changes

```bash
git push origin feature/my-feature
```

### Create Pull Request

1. Go to GitHub
2. Create Pull Request
3. Describe changes
4. Request review

## Environment Variables

Create `.env.local` in frontend directory:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=Sigma
VITE_DEBUG=true
```

Access in code:
```javascript
const apiUrl = import.meta.env.VITE_API_BASE_URL
```

## Troubleshooting

### Port 5173 Already in Use

```bash
# Use different port
npm run dev -- --port 5174

# Or kill process using port
lsof -ti:5173 | xargs kill -9
```

### Module Not Found

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Vite Cache Issues

```bash
# Clear Vite cache
rm -rf dist .vite

# Restart dev server
npm run dev
```

### API Calls Failing

1. Check Frappe backend is running
2. Verify API URL in browser console
3. Check Network tab for errors
4. Verify CSRF token in cookies

### Hot Module Replacement Not Working

```bash
# Restart dev server
npm run dev

# Check that port 5173 is accessible
# Try different port if needed
npm run dev -- --port 5174
```

## Performance Optimization

### Monitor Bundle Size

```bash
npm run build
# Check dist/ folder size
ls -lh dist/
```

### Analyze Bundle

Install `rollup-plugin-visualizer`:
```bash
npm install --save-dev rollup-plugin-visualizer
```

Add to `vite.config.js`:
```javascript
import { visualizer } from 'rollup-plugin-visualizer'

export default {
  plugins: [
    visualizer()
  ]
}
```

Then build and open `stats.html`.

## Testing Setup (Optional)

### Install Vitest

```bash
npm install --save-dev vitest @vue/test-utils jsdom
```

### Create Test File

`src/components/__tests__/MyComponent.spec.js`:
```javascript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import MyComponent from '../MyComponent.vue'

describe('MyComponent', () => {
  it('renders properly', () => {
    const wrapper = mount(MyComponent)
    expect(wrapper.text()).toContain('expected text')
  })
})
```

### Run Tests

```bash
npm run test
```

## Code Formatting

### Install Prettier

```bash
npm install --save-dev prettier
```

### Format Code

```bash
npx prettier --write src/
```

### Auto-format on Save

Configure in VS Code settings (see IDE Setup section).

## Debugging Tips

### Console Logging

```javascript
console.log('Debug:', variable)
console.error('Error:', error)
console.table(arrayOfObjects)
```

### Vue DevTools

1. Open Vue tab in DevTools
2. Select component
3. View props, data, computed
4. Edit data in real-time

### Network Debugging

1. Open Network tab
2. Filter by XHR
3. Click request to see details
4. Check request/response headers and body

### Source Maps

Enable in DevTools:
1. Settings > Sources
2. Enable "Enable JavaScript source maps"

## Useful Commands

```bash
# Development
npm run dev              # Start dev server
npm run build            # Build for production
npm run preview          # Preview production build
npm run lint             # Check code quality
npm run lint -- --fix    # Fix linting issues

# Package management
npm install              # Install dependencies
npm update               # Update packages
npm audit                # Check for vulnerabilities
npm audit fix            # Fix vulnerabilities

# Cleanup
npm cache clean --force  # Clear npm cache
rm -rf node_modules      # Remove node_modules
```

## Recommended Workflow

1. **Start Dev Server**
   ```bash
   npm run dev
   ```

2. **Open in Browser**
   - http://localhost:5173/

3. **Open IDE**
   - VS Code or WebStorm

4. **Open DevTools**
   - F12 in browser

5. **Edit Code**
   - Make changes in IDE
   - See live updates in browser

6. **Debug**
   - Use DevTools Console
   - Use Vue DevTools
   - Check Network tab

7. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: description"
   git push origin branch-name
   ```

## Resources

- **Node.js**: https://nodejs.org/
- **npm**: https://www.npmjs.com/
- **Vue 3**: https://vuejs.org/
- **Vite**: https://vitejs.dev/
- **VS Code**: https://code.visualstudio.com/

## Getting Help

- Check documentation files in frontend directory
- Review existing code for patterns
- Check browser console for errors
- Contact: info@prismod.co.ke

## Next Steps

1. ✅ Install Node.js
2. ✅ Install dependencies: `npm install`
3. ✅ Start dev server: `npm run dev`
4. ✅ Open browser: http://localhost:5173/
5. ✅ Read QUICKSTART.md
6. ✅ Start developing!

Happy coding! 🚀

