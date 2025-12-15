# 🚀 Vercel Setup - Step by Step Instructions

## ✅ Your Generated Secret Key
```
(+ny-r#jhv9f(kdpl_r69pt2se6%6r6z0(^67ivz2%%$b(kd0q
```

---

## 📝 Step 1: Add Environment Variables in Vercel

### Option A: Via Vercel Dashboard (EASIEST - Recommended)

1. **Open Vercel Dashboard:**
   - Click here: https://vercel.com/lagrimas-vince-ps-projects/topstyle-business/settings/environment-variables
   - Or go to: Vercel Dashboard → Your Project → Settings → Environment Variables

2. **Add these variables one by one:**

   | Variable Name | Value | Environment |
   |--------------|-------|-------------|
   | `SECRET_KEY` | `(+ny-r#jhv9f(kdpl_r69pt2se6%6r6z0(^67ivz2%%$b(kd0q` | Production, Preview, Development |
   | `DEBUG` | `False` | Production, Preview, Development |
   | `ALLOWED_HOSTS` | `*.vercel.app,topstyle-business-*.vercel.app` | Production, Preview, Development |

3. **Click "Save" after each variable**

### Option B: Via Vercel CLI

Run these commands in your terminal:

```bash
echo (+ny-r#jhv9f(kdpl_r69pt2se6%6r6z0(^67ivz2%%$b(kd0q | vercel env add SECRET_KEY production
echo False | vercel env add DEBUG production
echo "*.vercel.app,topstyle-business-*.vercel.app" | vercel env add ALLOWED_HOSTS production
```

---

## 🗄️ Step 2: Set Up PostgreSQL Database

SQLite doesn't work on Vercel. You **must** use PostgreSQL.

### Recommended: Supabase (Free, Easy, 2 minutes)

1. **Go to Supabase:**
   - Visit: https://supabase.com/dashboard/projects
   - Sign up or log in

2. **Create New Project:**
   - Click **"New Project"**
   - **Name:** `topstyle-business`
   - **Database Password:** Create a strong password (**SAVE THIS!**)
   - **Region:** Choose closest to you
   - Click **"Create new project"**
   - Wait ~2 minutes for setup

3. **Get Connection String:**
   - Go to **Settings** (gear icon in left sidebar)
   - Click **"Database"**
   - Scroll to **"Connection string"** section
   - Select **"URI"** tab
   - Copy the connection string (looks like):
     ```
     postgresql://postgres.[project-ref]:[YOUR-PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres
     ```

4. **Add to Vercel:**
   - Go back to Vercel Environment Variables
   - Add new variable:
     - **Name:** `DATABASE_URL`
     - **Value:** (paste the connection string you copied)
     - **Environment:** Production, Preview, Development
   - Click **"Save"**

---

## 🔄 Step 3: Run Database Migrations

After adding `DATABASE_URL`, run migrations:

1. **Pull environment variables:**
   ```bash
   vercel env pull .env.local
   ```

2. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

3. **Create admin user (optional):**
   ```bash
   python manage.py createsuperuser
   ```
   - Username: `admin` (or your choice)
   - Email: `admin@topstyle.com` (or your email)
   - Password: (create a strong password)

---

## 🚀 Step 4: Redeploy

After setting everything up, redeploy:

```bash
vercel --prod
```

This will redeploy with all new environment variables and database connection.

---

## ✅ Step 5: Verify Deployment

1. **Visit your app:**
   - Production URL: `https://topstyle-business-mw227psxo-lagrimas-vince-ps-projects.vercel.app`

2. **Test:**
   - ✅ Does the page load?
   - ✅ Can you access `/admin/`?
   - ✅ Can you log in?
   - ✅ Do static files load (CSS, images)?

---

## 🆘 Troubleshooting

### ❌ Database Connection Error

**Problem:** `django.db.utils.OperationalError: could not connect to server`

**Solutions:**
1. Verify `DATABASE_URL` is correct in Vercel
2. Check database is not paused (Supabase pauses inactive projects)
3. Ensure password in connection string matches your database password
4. Try using connection pooler URL (port 6543) instead of direct connection (port 5432)

### ❌ Static Files Not Loading

**Problem:** CSS/images not showing

**Solutions:**
1. Verify `collectstatic` ran: `python manage.py collectstatic --noinput`
2. Check `STATIC_ROOT` in settings.py
3. Verify WhiteNoise middleware is in `MIDDLEWARE` settings

### ❌ 500 Internal Server Error

**Problem:** Page shows 500 error

**Solutions:**
1. Check Vercel function logs: `vercel logs`
2. Verify all environment variables are set
3. Check database connection
4. Look for errors in Vercel Dashboard → Deployments → View Function Logs

---

## 📊 Quick Reference

| Item | Status | Action |
|------|--------|--------|
| Secret Key | ✅ Generated | Add to Vercel |
| DEBUG | ⏳ Pending | Set to `False` |
| ALLOWED_HOSTS | ⏳ Pending | Add to Vercel |
| Database | ⏳ Pending | Set up PostgreSQL |
| Migrations | ⏳ Pending | Run after DB setup |
| Redeploy | ⏳ Pending | Run `vercel --prod` |

---

## 🎯 Current Status

✅ **Deployment Complete** - App is deployed to Vercel  
⏳ **Environment Variables** - Need to be set  
⏳ **Database** - Need to be configured  
⏳ **Migrations** - Need to run  
⏳ **Final Redeploy** - After above steps  

---

## 📝 Next Steps

1. **Right now:** Add environment variables (Step 1)
2. **Next:** Set up PostgreSQL database (Step 2)
3. **Then:** Run migrations (Step 3)
4. **Finally:** Redeploy (Step 4)

**Estimated time:** 10-15 minutes total

---

**Need help?** Check the detailed guides:
- `setup_vercel_env.md` - Detailed setup guide
- `QUICK_SETUP_VERCEL.md` - Quick reference
















