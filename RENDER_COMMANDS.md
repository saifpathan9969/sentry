# 🚀 RENDER DEPLOYMENT COMMANDS

## **Quick Command Reference for Fresh Terminal**

### **Step 1: Update GitHub Repositories**
```powershell
# Navigate to your project directory
cd "C:\Users\saifu\OneDrive\Desktop\neural schema"

# Activate virtual environment
& ".venv/Scripts/Activate.ps1"

# Run update script
.\update-for-render.ps1
```

### **Step 2: Manual Git Updates (if script fails)**

**Update Frontend:**
```powershell
cd frontend
git add .
git commit -m "Update for Render deployment"
git push origin main
cd ..
```

**Update Backend:**
```powershell
cd backend  
git add .
git commit -m "Add Render configuration"
git push origin main
cd ..
```

### **Step 3: Render Backend Configuration**

**Service Settings:**
```
Name: neural-brain-backend
Environment: Python 3
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Environment Variables:**
```bash
DATABASE_URL=your-neon-postgresql-url-here
SECRET_KEY=your-super-secret-key-here
ENVIRONMENT=production
PROJECT_NAME=Neural Brain Security
CORS_ORIGINS=["https://neural-brain-security.vercel.app"]
```

### **Step 4: Initialize Database**
```bash
# In Render Shell
python create_production_owner.py
```

### **Step 5: Vercel Frontend Configuration**

**Project Settings:**
```
Framework: Vite
Root Directory: frontend
Build Command: npm run build
Output Directory: dist
```

**Environment Variables:**
```
VITE_API_BASE_URL=https://your-render-backend.onrender.com/api/v1
```

### **Step 6: Test Commands**

**Test Backend Health:**
```bash
curl https://your-render-backend.onrender.com/health
```

**Test Login:**
```powershell
$loginData = @{
    email = "saifullahpathan49@gmail.com"
    password = "sentry@779969"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "https://your-render-backend.onrender.com/api/v1/auth/login" -Method POST -Body $loginData -ContentType "application/json"

Write-Host "Login successful! Token: $($response.access_token.Substring(0,50))..."
```

---

## **🎯 Expected Results**

After following these commands:

✅ **Backend**: `https://neural-brain-backend.onrender.com`
✅ **Frontend**: `https://neural-brain-security.vercel.app`  
✅ **Database**: Neon PostgreSQL (no more SQLite issues)
✅ **Authentication**: Working perfectly
✅ **Neural Brain**: 3D visualization functional

---

## **🔑 Login Credentials**
- **Email**: `saifullahpathan49@gmail.com`
- **Password**: `sentry@779969`
- **Tier**: Enterprise (Full Access)

---

## **📞 Support**

If any command fails:
1. Check you're in the right directory
2. Ensure virtual environment is activated
3. Verify Git repositories are properly configured
4. Check network connection

**Follow RENDER_DEPLOYMENT_GUIDE.md for detailed step-by-step instructions!**