# Sigma Frontend - Deployment Guide

This guide covers deploying the Sigma Vue.js frontend to production on prismod.co.ke.

## Prerequisites

- Frappe bench environment set up
- Sigma app installed
- Node.js 16+ and npm installed
- SSH access to production server
- Git repository access

## Deployment Steps

### 1. Build the Frontend

On your local development machine:

```bash
cd apps/sigma/sigma/frontend
npm install
npm run build
```

This creates optimized production files in `../public/dist/`

### 2. Verify Build Output

Check that the build was successful:

```bash
ls -la ../public/dist/
```

You should see:
- `js/main.js` - Main application bundle
- `css/main.css` - Global styles
- `images/` - Optimized images
- `fonts/` - Web fonts

### 3. Commit Changes

```bash
cd /path/to/frappe-bench
git add apps/sigma/
git commit -m "Build: Update Sigma frontend production assets"
```

### 4. Push to Repository

```bash
git push origin main
```

### 5. Deploy to Production

SSH into the production server:

```bash
ssh user@prismod.co.ke
cd /home/frappe/frappe-bench
```

Pull the latest changes:

```bash
git pull origin main
```

Clear Frappe cache:

```bash
bench --site prismod.co.ke clear-cache
```

Restart Frappe:

```bash
bench restart
```

### 6. Verify Deployment

1. Open browser and navigate to: https://prismod.co.ke/app/sigma/
2. Check browser console (F12) for errors
3. Verify all pages load correctly
4. Test key functionality:
   - Login/logout
   - Dashboard loads
   - Case list displays
   - Navigation works

## Continuous Deployment (Optional)

### Using GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy Sigma Frontend

on:
  push:
    branches: [main]
    paths:
      - 'apps/sigma/sigma/frontend/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: |
          cd apps/sigma/sigma/frontend
          npm install
      
      - name: Build
        run: |
          cd apps/sigma/sigma/frontend
          npm run build
      
      - name: Deploy
        run: |
          # Add your deployment script here
          # e.g., SSH to server and pull changes
```

## Rollback Procedure

If deployment fails:

1. SSH to production server
2. Revert to previous commit:
```bash
cd /home/frappe/frappe-bench
git revert HEAD
git push origin main
```

3. Clear cache and restart:
```bash
bench --site prismod.co.ke clear-cache
bench restart
```

## Performance Optimization

### Asset Compression

Vite automatically minifies and compresses assets. Verify in production:

```bash
# Check file sizes
ls -lh ../public/dist/js/
ls -lh ../public/dist/css/
```

### Caching Headers

Configure Frappe to set proper cache headers for static assets:

In `frappe-bench/config/nginx.conf`:

```nginx
location /app/sigma/dist/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### CDN Integration (Optional)

For faster global delivery, configure a CDN:

1. Upload `public/dist/` to CDN
2. Update asset URLs in `hooks.py`:

```python
app_include_js = [
    "https://cdn.example.com/sigma/dist/js/main.js"
]
app_include_css = [
    "https://cdn.example.com/sigma/dist/css/main.css"
]
```

## Monitoring

### Check Application Logs

```bash
tail -f /home/frappe/frappe-bench/logs/error.log
```

### Monitor Browser Console

1. Open https://prismod.co.ke/app/sigma/
2. Press F12 to open Developer Tools
3. Check Console tab for errors
4. Check Network tab for failed requests

### Performance Metrics

Use browser DevTools:
1. Open Performance tab
2. Record page load
3. Analyze metrics:
   - First Contentful Paint (FCP)
   - Largest Contentful Paint (LCP)
   - Cumulative Layout Shift (CLS)

## Troubleshooting

### Assets Not Loading

1. Clear browser cache: Ctrl+Shift+Delete
2. Hard refresh: Ctrl+Shift+R
3. Check that `public/dist/` exists on server
4. Verify `hooks.py` asset paths are correct

### API Calls Failing

1. Check CSRF token in cookies
2. Verify Frappe backend is running
3. Check browser console for CORS errors
4. Verify user has required permissions

### Blank Page

1. Check browser console for JavaScript errors
2. Verify `index.html` is being served
3. Check that Vue app is mounting to `#app` element
4. Verify all dependencies are loaded

### Slow Performance

1. Check network tab for slow requests
2. Verify API responses are fast
3. Check for memory leaks in DevTools
4. Optimize images and assets

## Maintenance

### Regular Updates

Keep dependencies updated:

```bash
cd apps/sigma/sigma/frontend
npm update
npm audit fix
```

### Testing Before Deployment

Always test in staging first:

```bash
# Build
npm run build

# Test locally
npm run preview

# Run tests (if available)
npm run test
```

## Backup

Before major deployments, backup the current state:

```bash
cd /home/frappe/frappe-bench
git tag backup-$(date +%Y%m%d-%H%M%S)
git push origin --tags
```

## Support

For deployment issues:
- Check Frappe documentation: https://frappeframework.com
- Review error logs
- Contact: info@prismod.co.ke

## Checklist

- [ ] Build completes without errors
- [ ] All assets are generated in `public/dist/`
- [ ] Changes committed and pushed
- [ ] Production server updated
- [ ] Cache cleared
- [ ] Frappe restarted
- [ ] Application loads in browser
- [ ] All pages accessible
- [ ] API calls working
- [ ] No console errors
- [ ] Performance acceptable

