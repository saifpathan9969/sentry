# 🚀 VERCEL FRONTEND DEPLOYMENT GUIDE

## **📋 STEP-BY-STEP DEPLOYMENT**

### **1. Update GitHub Frontend Repository**

First, push the updated API client to your frontend repository:

```powershell
# Navigate to frontend directory
cd frontend

# Add and commit changes
git add .
git commit -m "Update API URL for Render backend"
git push origin main
```

### **2. Deploy to Vercel**

#### **Option A: Vercel Dashboard (Recommended)**

1. **Go to Vercel**: https://vercel.com
2. **Sign in** with your GitHub account
3. **Click "New Project"**
4. **Import your repository**: `saifpathan9969/sentry-frontend`
5. **Configure project settings**:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend` (IMPORTANT!)
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

6. **Add Environment Variables**:
   ```
   VITE_API_BASE_URL=https://sentry-backend-1.onrender.com/api/v1
   ```

7. **Click "Deploy"**

#### **Option B: Vercel CLI (Alternative)**

```powershell
# Install Vercel CLI
npm i -g vercel

# Navigate to frontend directory
cd frontend

# Deploy
vercel

# Follow prompts:
# - Link to existing project? No
# - Project name: sentry-frontend
# - Directory: ./
# - Override settings? Yes
# - Build command: npm run build
# - Output directory: dist
# - Development command: npm run dev
```

### **3. Set Environment Variables in Vercel**

After deployment, add the environment variable:

1. **Go to your Vercel project dashboard**
2. **Click "Settings" tab**
3. **Click "Environment Variables"**
4. **Add new variable**:
   - **Name**: `VITE_API_BASE_URL`
   - **Value**: `https://sentry-backend-1.onrender.com/api/v1`
   - **Environment**: Production, Preview, Development

5. **Click "Save"**
6. **Redeploy** (go to Deployments tab → click "..." → Redeploy)

### **4. Update Backend CORS Settings**

Once your Vercel app is deployed, update your Render backend:

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Find your `sentry-backend-1` service**
3. **Go to Environment tab**
4. **Add/Update environment variable**:
   ```
   CORS_ORIGINS=["https://your-vercel-app.vercel.app","http://localhost:3000","http://localhost:5173"]
   ```
   Replace `your-vercel-app` with your actual Vercel app name.

5. **Save and redeploy**

## **🎯 EXPECTED VERCEL URLS**

Your Vercel app will be available at:
- **Production**: `https://sentry-frontend.vercel.app`
- **Or custom**: `https://your-project-name.vercel.app`

## **🧪 TESTING YOUR DEPLOYMENT**

### **1. Test Frontend**
Visit your Vercel URL and verify:
- ✅ Page loads correctly
- ✅ Login form appears
- ✅ No console errors

### **2. Test Backend Connection**
1. **Open browser console** (F12)
2. **Go to Network tab**
3. **Try to login** with:
   - Email: `saifullahpathan49@gmail.com`
   - Password: `Sentry@779969`
4. **Check network requests** - should see calls to `sentry-backend-1.onrender.com`

### **3. Test Complete Flow**
- ✅ Registration works
- ✅ Login works
- ✅ Dashboard loads
- ✅ Neural Brain visualization appears
- ✅ Scan creation works

## **🔧 TROUBLESHOOTING**

### **CORS Errors**
If you see CORS errors:
1. Update CORS_ORIGINS in Render with your exact Vercel URL
2. Redeploy backend
3. Clear browser cache

### **API Connection Issues**
If API calls fail:
1. Check environment variable is set correctly
2. Verify backend is running: https://sentry-backend-1.onrender.com/health
3. Check browser console for errors

### **Build Errors**
If Vercel build fails:
1. Check build logs in Vercel dashboard
2. Ensure `frontend` is set as root directory
3. Verify package.json has correct scripts

## **📱 FINAL VERIFICATION**

Once deployed, test this complete flow:

1. **Visit your Vercel URL**
2. **Register a new account** (or login with owner account)
3. **Navigate to dashboard**
4. **Create a new scan**
5. **View Neural Brain visualization**
6. **Check scan results**

## **🎉 SUCCESS INDICATORS**

✅ **Frontend loads** at Vercel URL
✅ **API calls work** (check Network tab)
✅ **Authentication works** (login/register)
✅ **Neural Brain renders** (3D visualization)
✅ **Scans can be created** and viewed

## **🚀 NEXT STEPS AFTER DEPLOYMENT**

1. **Custom domain** (optional): Add your own domain in Vercel
2. **Analytics**: Add Vercel Analytics
3. **Performance**: Monitor Core Web Vitals
4. **SEO**: Add meta tags and sitemap

Your **AI Pentest Brain** platform will be fully live and operational! 🧠🚀

---

## **📞 Support URLs**

- **Frontend**: Your Vercel URL
- **Backend**: https://sentry-backend-1.onrender.com
- **Health Check**: https://sentry-backend-1.onrender.com/health

**Ready to deploy your Neural Brain Security Platform!** 🎊