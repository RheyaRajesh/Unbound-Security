# Deployment Guide

## Streamlit Cloud Deployment

This app is ready to deploy on Streamlit Cloud (free hosting).

### Step 1: Push to GitHub

1. Initialize git repository (if not already):
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Agentic Workflow Builder"
   ```

2. Create a new repository on GitHub (don't initialize with README)

3. Push your code:
   ```bash
   git remote add origin https://github.com/yourusername/your-repo-name.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"
4. Fill in:
   - **Repository:** Select your repository
   - **Branch:** `main`
   - **Main file path:** `streamlit_app.py`
5. Click "Deploy!"

### Step 3: Configure Secrets (Optional)

If you want to override the API key via environment variables:

1. In Streamlit Cloud, go to your app settings
2. Click "Secrets"
3. Add:
   ```toml
   UNBOUND_API_KEY = "your_api_key_here"
   UNBOUND_API_BASE = "https://api.getunbound.ai/v1"
   ```

**Note:** The API key is already configured in `config.py`, so this step is optional.

### Step 4: Access Your App

Your app will be available at:
```
https://your-app-name.streamlit.app
```

## Alternative: Local Deployment

For local deployment or other platforms:

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the app:
   ```bash
   streamlit run app.py
   ```

3. Access at `http://localhost:8501`

## Environment Variables

The app uses these environment variables (all optional since defaults are set):

- `UNBOUND_API_KEY`: Unbound API key (default: already set in config.py)
- `UNBOUND_API_BASE`: API base URL (default: https://api.getunbound.ai/v1)

## Storage

The app creates two directories for local storage:
- `workflows/` - Saved workflow definitions
- `executions/` - Execution history

These are automatically created on first run. For production, consider using a database instead of file storage.

## Troubleshooting

**App won't start:**
- Check that all dependencies are installed
- Verify Python version (3.8+)
- Check Streamlit Cloud logs for errors

**API errors:**
- Verify API key is correct
- Check API endpoint is accessible
- Review execution logs in the app

**Storage issues:**
- Ensure write permissions in the app directory
- Check disk space
- For Streamlit Cloud, storage is ephemeral (resets on redeploy)
