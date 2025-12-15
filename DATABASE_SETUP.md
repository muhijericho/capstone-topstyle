# 🗄️ Database Setup - Quick Guide

## ⚡ Fastest Option: Supabase (2 minutes)

### Step 1: Create Supabase Account
1. Go to: https://supabase.com/dashboard/projects
2. Sign up or log in (free)

### Step 2: Create Project
1. Click **"New Project"**
2. **Organization:** (select or create one)
3. **Name:** `topstyle-business`
4. **Database Password:** Create a strong password
   - **⚠️ SAVE THIS PASSWORD!** You'll need it for the connection string
   - Example: `MySecurePass123!@#`
5. **Region:** Choose closest to you (e.g., `Southeast Asia (Singapore)`)
6. **Pricing Plan:** Free
7. Click **"Create new project"**
8. **Wait 2 minutes** for database to be created

### Step 3: Get Connection String
1. Once project is ready, go to **Settings** (gear icon in sidebar)
2. Click **"Database"** in settings menu
3. Scroll down to **"Connection string"** section
4. Click on **"URI"** tab
5. You'll see something like:
   ```
   postgresql://postgres.[ref]:[YOUR-PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres
   ```
6. **Replace `[YOUR-PASSWORD]`** with the password you created in Step 2
7. **Copy the entire connection string**

### Step 4: Add to Vercel
Once you have the connection string, I'll add it automatically. Just paste it here or run:

```bash
echo "YOUR_CONNECTION_STRING_HERE" | vercel env add DATABASE_URL production
echo "YOUR_CONNECTION_STRING_HERE" | vercel env add DATABASE_URL preview
echo "YOUR_CONNECTION_STRING_HERE" | vercel env add DATABASE_URL development
```

---

## 🔄 Alternative: Neon (Also Free)

1. Go to: https://neon.tech
2. Sign up/Login
3. Click **"Create a project"**
4. Name: `topstyle-business`
5. Region: (choose closest)
6. Click **"Create project"**
7. Copy the connection string from dashboard
8. Add to Vercel as `DATABASE_URL`

---

## ✅ After Database is Set Up

Once you have the `DATABASE_URL`, I'll:
1. ✅ Add it to Vercel environment variables
2. ✅ Pull environment variables locally
3. ✅ Run database migrations
4. ✅ Create admin user
5. ✅ Redeploy to Vercel

---

**Ready?** Go to Supabase now: https://supabase.com/dashboard/projects


 -+

 ..+

 











