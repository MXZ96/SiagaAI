# Deployment Guide - SiagaAI

## Architecture
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────┐
│   Frontend      │────▶│   Backend       │────▶│  MongoDB    │
│   (Vercel)     │     │   (Railway)     │     │  (Atlas)    │
└─────────────────┘     └─────────────────┘     └─────────────┘
```

## Prerequisites
- Vercel account (frontend)
- Railway account (backend)
- MongoDB Atlas (already configured)

---

## Step 1: Deploy Backend ke Railway

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

### 1.2 Deploy ke Railway
1. Login to [Railway](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Configure:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
5. Add Environment Variables (di Railway dashboard → Variables tab):
   - `GOOGLE_CLIENT_ID`: your Google Client ID
   - `JWT_SECRET`: generate random string (32+ chars)
   - `MONGODB_URI`: your MongoDB Atlas connection string
   - `FLASK_ENV`: production
6. Click "Deploy"

### 1.3 Get Backend URL
After deployment, you'll get a URL like:
`https://siagaai-backend-production.up.railway.app`

---

## Step 2: Deploy Frontend ke Vercel

### 2.1 Update Environment Variables
Edit `frontend/.env.production`:
```env
VITE_GOOGLE_CLIENT_ID=483084676706-030qqlcte3gsfo9gt73qu28qpk3k48ka.apps.googleusercontent.com
VITE_API_URL=https://siagaai-production.up.railway.app
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
   - `https://siagaai-production.up.railway.app/api/auth/google`
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
- Check Railway logs for errors
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
