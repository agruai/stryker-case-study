# Git Commit Instructions

Due to file locking issues, please run these commands manually in your terminal:

## Setup (if not already done):
```bash
git config user.name "omenworks"
git config user.email "33125782+omenworks@users.noreply.github.com"
git remote add origin https://github.com/omenworks/stryker-case-study.git
```

## Step-by-step Commits:

### 1. Documentation
```bash
git add .gitignore README.md SETUP.md DEMO_GUIDE.md
git commit -m "docs: Add project documentation and setup guides"
```

### 2. Backend Dependencies
```bash
git add backend/requirements.txt backend/create_sample_invoices.py
git commit -m "feat: Add backend dependencies and sample invoice generator"
```

### 3. Backend Application
```bash
git add backend/app.py
git commit -m "feat: Implement Flask backend with OpenAI integration and database"
```

### 4. Frontend Configuration
```bash
git add frontend/package.json frontend/tsconfig.json frontend/next.config.js frontend/next-env.d.ts frontend/.gitignore
git commit -m "feat: Add Next.js frontend configuration"
```

### 5. Frontend Application
```bash
git add frontend/app/
git commit -m "feat: Implement React/Next.js frontend with invoice upload and display"
```

### 6. Startup Scripts
```bash
git add start_backend.bat start_frontend.bat
git commit -m "chore: Add startup scripts for Windows"
```

### 7. Push to GitHub
```bash
git branch -M main
git push -u origin main
```

## Troubleshooting:

If you get "unable to write new index file" error:
1. Close all IDEs (VS Code, Cursor, etc.)
2. Close File Explorer windows showing this directory
3. Run PowerShell/CMD as Administrator
4. Try the commands again

Alternatively, you can commit everything at once:
```bash
git add .
git commit -m "Initial commit: Invoice extraction app with Flask backend and Next.js frontend"
git branch -M main
git push -u origin main
```
