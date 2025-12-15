# ⚡ Quick Vercel Setup - Copy & Paste Guide

## 🎯 TL;DR - Do This Now

### 1️⃣ Set Environment Variables

Go to: https://vercel.com/lagrimas-vince-ps-projects/topstyle-business/settings/environment-variables

**Copy and paste these (one by one):**

```
SECRET_KEY
(+ny-r#jhv9f(kdpl_r69pt2se6%6r6z0(^67ivz2%%$b(kd0q

DEBUG
False

ALLOWED_HOSTS
*.vercel.app,topstyle-business-*.vercel.app
```

### 2️⃣ Create Database (Choose ONE)

#### 🟢 EASIEST: Supabase (2 minutes)
1. Go to: https://supabase.com/dashboard/projects
2. Click **"New Project"**
3. Name: `topstyle-business`
4. Password: (create a strong password - **SAVE IT!**)
5. Region: (closest to you)
6. Click **"Create new project"**
7. Wait 2 minutes
8. Go to **Settings → Database**
9. Scroll to **"Connection string" → "URI"**
10. Copy the connection string
11. Add as `DATABASE_URL` in Vercel

### 3️⃣ Run Migrations

After adding `DATABASE_URL`, run:

```bash
vercel env pull .env.local
python manage.py migrate
python manage.py createsuperuser
```

### 4️⃣ Redeploy

```bash
vercel --prod
```

## ✅ Done!

Your app should be live at:
`https://topstyle-business-mw227psxo-lagrimas-vince-ps-projects.vercel.app`

---

**Need help?** Check `setup_vercel_env.md` for detailed instructions.
















