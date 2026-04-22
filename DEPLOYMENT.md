# UtilityGuard Deployment Guide 🚀

Follow these steps to host your application on **Streamlit Community Cloud** so everyone can access it via a live URL.

## Step 1: Create a GitHub Repository
1. Go to [github.com/new](https://github.com/new).
2. Name your repository (e.g., `UtilityGuard-Platform`).
3. Keep it **Public** (or Private if you have Streamlit Cloud access for private repos).
4. Do NOT initialize with a README (we have our own code).

## Step 2: Push your Code to GitHub
Open your terminal (PowerShell) in the project directory and run:
```bash
git init
git add .
git commit -m "Initial Deployment Release"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
git push -u origin main
```
*(Replace YOUR_USERNAME and YOUR_REPOSITORY_NAME with your actual GitHub details)*

## Step 3: Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io).
2. Click **"New app"**.
3. Select your repository: `YOUR_USERNAME/YOUR_REPOSITORY_NAME`.
4. Branch: `main`.
5. Main file path: `app.py`.
6. Click **"Deploy!"**.

## Step 4: Configure Secrets (IMPORTANT)
Your app will fail initially because the `.env` file is hidden. You must add these manually:
1. In your Streamlit Cloud dashboard, go to your app's **Settings**.
2. Click on **Secrets**.
3. Copy and paste the following (filling in your real key):

```toml
MISTRAL_API_KEY = "YOUR_MISTRAL_KEY_HERE"
HOST_USERNAME = "admin"
HOST_PASSWORD = "password123"
```

---

### FAQ: Troubleshooting
- **ModuleNotFoundError:** Ensure `requirements.txt` is in the root and contains all packages.
- **SQLite Database:** Remember that registrations on Streamlit Cloud are temporary. For a permanent database, you'll eventually need to connect to a service like Supabase.
