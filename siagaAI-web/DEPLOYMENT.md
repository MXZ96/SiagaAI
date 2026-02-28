# Deployment Guide - SiagaAI

## Architecture
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────┐
│   Frontend      │────▶│   Backend       │────▶│  MongoDB    │
│   (Vercel)     │     │   (Render)      │     │  (Atlas)    │
└─────────────────┘     └─────────────────┘     └─────────────┘
```

## Prerequisites
- Vercel account (frontend)
- Render account (backend)
- MongoDB Atlas (already configured)

---

## Step 1: Deploy Backend ke Render

### 1.1 Push Code ke GitHub
```bash
# Create new repository on GitHub
# Then push your code:
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/siagaAI.git
git push -u origin main
```

### 1.2 Deploy ke Render
1. Login to [Render](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: siagaai-backend
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
5. Add Environment Variables:
   - `GOOGLE_CLIENT_ID`: your Google Client ID
   - `JWT_SECRET`: generate random string (32+ chars)
   - `MONGODB_URI`: `mongodb+srv://editormxz_db_user:WQC796PGk7QfGylL@siagaai.m0pmtec.mongodb.net/?appName=siagaAI`
   - `FLASK_ENV`: production
6. Click "Create Web Service"

### 1.3 Get Backend URL
After deployment, you'll get a URL like:
`https://siagaai-backend.onrender.com`

---

## Step 2: Deploy Frontend ke Vercel

### 2.1 Update Environment Variables
Edit `frontend/.env.production`:
```env
VITE_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
VITE_API_URL=https://siagaai-backend.onrender.com
```

### 2.2 Deploy ke Vercel
1. Login to [Vercel](https://vercel.com)
2. Click "Add New..." → "Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Add Environment Variables (in Vercel dashboard):
   - `VITE_GOOGLE_CLIENT_ID`: your Google Client ID
   - `VITE_API_URL`: your Render backend URL
6. Click "Deploy"

---

## Step 3: Update Google OAuth Redirect URIs

In Google Cloud Console:
1. Go to **APIs & Services** → **Credentials**
2. Click your OAuth 2.0 Client
3. Add to **Authorized redirect URIs**:
   - `https://siagaai-backend.onrender.com/api/auth/google`
4. Add to **Authorized JavaScript origins**:
   - `https://your-vercel-app.vercel.app`

---

## Important Notes

### CORS Configuration
The backend already has CORS enabled, but make sure to update if needed:
```python
# In app.py
CORS(app, origins=["https://your-vercel-app.vercel.app"])
```

### Environment Variables Summary

| Variable | Backend | Frontend |
|----------|---------|----------|
| GOOGLE_CLIENT_ID | ✅ | ✅ |
| JWT_SECRET | ✅ | - |
| MONGODB_URI | ✅ | - |
| VITE_API_URL | - | ✅ |
| FLASK_ENV | ✅ | - |

---

## Troubleshooting

### 500 Error on API
- Check Render logs for errors
- Verify environment variables are set correctly

### CORS Error
- Ensure frontend URL is in CORS origins
- Check that backend is running

### MongoDB Connection Error
- Verify MONGODB_URI is correct
- Check IP whitelist in MongoDB Atlas

### Google Login Not Working
- Verify GOOGLE_CLIENT_ID matches in both places
- Check authorized redirect URIs in Google Cloud Console
