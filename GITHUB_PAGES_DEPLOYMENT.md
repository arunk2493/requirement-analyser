# GitHub Pages Deployment Guide

## Overview
This project is set up to automatically deploy to GitHub Pages using GitHub Actions.

## Prerequisites
- GitHub account with the repository `arunk2493/requirement-analyser`
- Repository should be public (or you have GitHub Pages enabled in your plan)

## Setup Instructions

### 1. Enable GitHub Pages
1. Go to your repository on GitHub
2. Navigate to **Settings** → **Pages**
3. Under "Build and deployment":
   - **Source**: Select "GitHub Actions"
   - This will trigger the automatic deployment

### 2. Repository Structure
```
requirement-analyser/
├── frontend/          # React/Vite frontend
│   ├── package.json
│   ├── vite.config.js (configured with base: "/requirement-analyser/")
│   └── src/
├── backend/           # Python Flask backend (not deployed on Pages)
├── .github/
│   └── workflows/
│       └── deploy.yml # GitHub Actions workflow
└── README.md
```

### 3. Automatic Deployment
The GitHub Actions workflow (`deploy.yml`) will:
- Trigger on push to `main` or `login-dev` branches
- Install Node.js dependencies
- Build the frontend using Vite
- Upload the build artifacts
- Deploy to GitHub Pages automatically

### 4. Deployment URL
Your site will be available at:
```
https://arunk2493.github.io/requirement-analyser/
```

### 5. Manual Trigger (Optional)
To manually trigger a deployment:
1. Go to **Actions** tab in your repository
2. Click "Deploy to GitHub Pages" workflow
3. Click **"Run workflow"** → **"Run workflow"** button

## Features Configured

✅ **Automatic Deployment**
- Triggers on push to `main` or `login-dev`
- Full CI/CD pipeline with Node.js build

✅ **Performance Optimizations**
- Minified build using Terser
- Production build output to `dist/` folder
- Caching of Node modules for faster builds

✅ **Correct Base Path**
- Frontend configured with `base: "/requirement-analyser/"` in vite.config.js
- All assets will load correctly from the subdirectory

## Important Notes

⚠️ **Backend API**
- This deployment only includes the frontend (React/Vite)
- The backend API must be hosted separately (e.g., Heroku, AWS, DigitalOcean, etc.)
- Update the API base URL in `frontend/src/api/api.js` to point to your deployed backend

⚠️ **CORS Settings**
- When integrating with the backend, ensure CORS is configured to allow requests from:
  ```
  https://arunk2493.github.io/requirement-analyser/
  ```

## Build Locally (Optional)

To build and test locally:
```bash
cd frontend
npm install
npm run build
npm run preview
```

This will create a `dist/` folder with the production build.

## Troubleshooting

### Workflow Failing?
1. Check **Actions** tab → **Deploy to GitHub Pages** workflow
2. Click on the failed run to see the error logs
3. Common issues:
   - Missing `package-lock.json` - Run `npm install` locally first
   - Node version mismatch - The workflow uses Node 18
   - Dependencies not installing - Check `frontend/package.json` for errors

### Site not loading?
1. Verify the repository is public
2. Check that GitHub Pages is enabled in Settings
3. Wait 1-2 minutes after pushing changes
4. Clear browser cache and hard refresh

### Assets returning 404?
- Make sure `vite.config.js` has `base: "/requirement-analyser/"`
- The base path must match your repository name

## Next Steps

1. **Push the code** to your GitHub repository
2. **GitHub Actions** will automatically build and deploy
3. **Visit** https://arunk2493.github.io/requirement-analyser/
4. **Configure backend API** URL if needed

---

For more information on GitHub Pages: https://docs.github.com/en/pages
