# Frontend Login Debug Guide

## The Problem
Backend login works perfectly (confirmed via API test), but frontend shows "Invalid username or password".

## Root Cause
This is a **frontend issue**, not a backend issue. Possible causes:
1. Frontend is cached (old version)
2. Frontend is pointing to wrong backend URL
3. CORS blocking the request
4. Network error

## Quick Fix Steps

### Step 1: Hard Refresh the Frontend
1. Go to https://sentry-brown-xi.vercel.app
2. **Hard refresh**: 
   - Windows: `Ctrl + Shift + R`
   - Mac: `Cmd + Shift + R`
3. Or **Clear cache**:
   - Windows: `Ctrl + Shift + Delete`
   - Mac: `Cmd + Shift + Delete`
   - Select "Cached images and files"
   - Click "Clear data"

### Step 2: Try Incognito/Private Window
1. Open a new incognito/private window
2. Go to https://sentry-brown-xi.vercel.app
3. Try logging in
4. If it works → Cache issue (clear cache in normal window)
5. If it doesn't work → Continue to Step 3

### Step 3: Check Browser Console
1. Open the app: https://sentry-brown-xi.vercel.app
2. Press `F12` to open DevTools
3. Go to **Console** tab
4. Try to login
5. Look for errors (red text)

**What to look for**:
- `CORS error` → Backend CORS issue
- `Network error` → Can't reach backend
- `404 Not Found` → Wrong API URL
- `Failed to fetch` → Network/CORS issue
- Any red error messages

### Step 4: Check Network Tab
1. In DevTools, go to **Network** tab
2. Try to login
3. Look for the login request (should be POST to `/auth/login`)
4. Click on it to see details

**Check**:
- **Request URL**: Should be `https://sentry-backend-1.onrender.com/api/v1/auth/login`
- **Status Code**: 
  - `200` = Success (but frontend not handling it?)
  - `400` = Bad request (wrong credentials format)
  - `401` = Invalid credentials
  - `0` or `(failed)` = Network/CORS error
- **Response**: Click "Response" tab to see error message

### Step 5: Check API URL Configuration
The frontend should be pointing to: `https://sentry-backend-1.onrender.com/api/v1`

**To verify**:
1. Open DevTools Console
2. Type: `localStorage.getItem('api_url')`
3. Or check the Network tab request URL

## Common Issues and Solutions

### Issue 1: CORS Error
**Symptoms**: 
- Console shows: "Access to fetch at '...' from origin '...' has been blocked by CORS policy"
- Network tab shows status `(failed)` or `0`

**Solution**: Backend CORS needs to allow Vercel domain
- Backend should allow: `https://sentry-brown-xi.vercel.app`
- Check `backend/app/main.py` CORS settings

### Issue 2: Wrong Backend URL
**Symptoms**:
- Network tab shows 404 Not Found
- Request going to wrong URL

**Solution**: Check `frontend/src/api/client.ts`
- Should have: `https://sentry-backend-1.onrender.com/api/v1`
- Not: `http://localhost:8000/api/v1`

### Issue 3: Cached Old Version
**Symptoms**:
- Works in incognito but not in normal window
- Console shows old code

**Solution**: Clear browser cache completely
- Ctrl+Shift+Delete → Clear everything
- Or use incognito window

### Issue 4: Backend Cold Start
**Symptoms**:
- First login attempt fails
- Second attempt works
- Network tab shows very long wait time (30+ seconds)

**Solution**: Wait and try again
- Render free tier "sleeps" after inactivity
- Takes 30-60 seconds to wake up
- Just wait and retry

## Test Backend Directly

To confirm backend is working, run this PowerShell command:

```powershell
$body = @{
    email = "saifullahpathan49@gmail.com"
    password = "Sentry@779969"
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://sentry-backend-1.onrender.com/api/v1/auth/login" -Method Post -Body $body -ContentType "application/json"
```

**Expected output**:
```
user         : @{id=...; email=saifullahpathan49@gmail.com; tier=enterprise; ...}
access_token : eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
refresh_token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

If this works but frontend doesn't → Frontend issue (cache, CORS, or wrong URL)

## What to Report Back

Please check and report:

1. **Hard refresh result**: Did it help? (Yes/No)
2. **Incognito result**: Does it work in incognito? (Yes/No)
3. **Console errors**: Copy any red error messages
4. **Network tab**:
   - Request URL: (copy the full URL)
   - Status code: (200, 400, 401, 0, failed?)
   - Response: (copy the error message if any)
5. **Backend test**: Does the PowerShell command work? (Yes/No)

With this information, I can pinpoint the exact issue and fix it.

## Quick Checklist

- [ ] Tried hard refresh (Ctrl+Shift+R)
- [ ] Tried clearing cache completely
- [ ] Tried incognito/private window
- [ ] Checked browser console for errors
- [ ] Checked network tab for failed requests
- [ ] Tested backend directly with PowerShell (works!)
- [ ] Reported findings

## Most Likely Solution

Based on the symptoms, the most likely issue is:

**Cached frontend code** - You're running an old version of the frontend that has bugs or wrong configuration.

**Solution**: 
1. Clear browser cache completely
2. Hard refresh the page
3. Or use incognito window
4. If still not working, we may need to redeploy the frontend
