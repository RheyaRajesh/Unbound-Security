# Git Commands for Pushing to GitHub

## Step 1: Initialize Git Repository (if not already done)

```bash
git init
```

## Step 2: Add All Files

```bash
git add .
```

## Step 3: Create Initial Commit

```bash
git commit -m "Initial commit: Agentic Workflow Builder"
```

## Step 4: Create GitHub Repository

1. Go to [github.com](https://github.com)
2. Click the "+" icon in the top right
3. Select "New repository"
4. Name it (e.g., "agentic-workflow-builder")
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

## Step 5: Add Remote and Push

After creating the repository on GitHub, GitHub will show you commands. Use these:

```bash
# Add remote (replace YOUR_USERNAME and REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

## Alternative: If you already have a GitHub repo

If you already created the repository, just use:

```bash
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
git branch -M main
git push -u origin main
```

## Full Command Sequence (Copy-Paste Ready)

Replace `YOUR_USERNAME` and `REPO_NAME` with your actual values:

```bash
git init
git add .
git commit -m "Initial commit: Agentic Workflow Builder"
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
git branch -M main
git push -u origin main
```

## If You Need to Authenticate

If GitHub asks for credentials:
- **Username**: Your GitHub username
- **Password**: Use a Personal Access Token (not your GitHub password)
  - Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
  - Generate new token with `repo` permissions
  - Use that token as the password

## Future Updates

After the initial push, for future updates:

```bash
git add .
git commit -m "Your commit message"
git push
```
