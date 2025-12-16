# 🚀 Vercel Environment Setup Guide

## ✅ Generated Secret Key

Your Django secret key has been generated:
```
(+ny-r#jhv9f(kdpl_r69pt2se6%6r6z0(^67ivz2%%$b(kd0q
```

## 📋 Step 1: Set Environment Variables in Vercel

1. **Go to Vercel Dashboard:**
   - Visit: https://vercel.com/lagrimas-vince-ps-projects/topstyle-business/settings/environment-variables

2. **Add these environment variables:**

### Required Variables:

```env
SECRET_KEY=(+ny-r#jhv9f(kdpl_r69pt2se6%6r6z0(^67ivz2%%$b(kd0q
DEBUG=False
ALLOWED_HOSTS=*.vercel.app,topstyle-business-*.vercel.app
```

### Database (Add after Step 2):
```env
DATABASE_URL=<will-be-added-after-database-setup>
```

### Optional (if using email):
```env
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

### Optional (if using Twilio):
```env
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_API_KEY=your_twilio_api_key
```

**⚠️ Important:** Set all variables for **Production**, **Preview**, and **Development** environments.

---

## 🗄️ Step 2: Set Up PostgreSQL Database

You have **3 options**:

### Option A: Vercel Postgres (Recommended - Easiest)

1. Go to: https://vercel.com/lagrimas-vince-ps-projects/topstyle-business/storage
2. Click **"Create Database"**
3. Select **"Postgres"**
4. Choose a name (e.g., `topstyle-db`)
5. Select region closest to you
6. Click **"Create"**
7. Once created, go to **"Connect"** tab
8. Copy the **Connection String** (it looks like: `postgres://user:pass@host:port/db`)
9. Add it as `DATABASE_URL` in environment variables

### Option B: Supabase (Free Tier)

1. Go to: https://supabase.com
2. Sign up/Login
3. Click **"New Project"**
4. Fill in details:
   - Name: `topstyle-business`
   - Database Password: (create a strong password)
   - Region: (choose closest)
5. Wait for project to be created (~2 minutes)
6. Go to **Settings → Database**
7. Scroll to **"Connection string"**
8. Copy the **URI** connection string
9. Format: `postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres`
10. Add it as `DATABASE_URL` in Vercel environment variables

### Option C: Neon (Free Tier)

1. Go to: https://neon.tech
2. Sign up/Login
3. Click **"Create a project"**
4. Fill in details:
   - Project name: `topstyle-business`
   - Region: (choose closest)
5. Click **"Create project"**
6. Copy the **Connection string** from the dashboard
7. Format: `postgresql://user:pass@host.neon.tech/db?sslmode=require`
8. Add it as `DATABASE_URL` in Vercel environment variables

---

## 🔄 Step 3: Run Database Migrations

After setting up the database and adding `DATABASE_URL`:

### Method 1: Via Vercel CLI (Local)

1. Pull environment variables:
   ```bash
   vercel env pull .env.local
   ```

2. Run migrations locally (connecting to remote DB):
   ```bash
   python manage.py migrate
   ```

3. Create a superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```

### Method 2: Via Vercel Dashboard

1. Go to your project dashboard
2. Use Vercel's console/deployment logs
3. Or create a one-time build script

### Method 3: Create Migration Build Command

I can help you set up a build command that runs migrations automatically.

---

## 🚀 Step 4: Redeploy

After setting environment variables and database:

```bash
vercel --prod
```

This will redeploy with new environment variables.

---

## ✅ Step 5: Verify Deployment

1. Visit your app: `https://topstyle-business-mw227psxo-lagrimas-vince-ps-projects.vercel.app`
2. Check if it loads
3. Try accessing admin: `/admin/`
4. Test login functionality

---

## 🆘 Troubleshooting

### Database Connection Error
- Verify `DATABASE_URL` is correct
- Check database allows connections from Vercel IPs
- Ensure database is active (not paused)

### Static Files Not Loading
- Ensure `collectstatic` ran successfully
- Check `STATIC_ROOT` in settings
- Verify WhiteNoise middleware is enabled

### 500 Internal Server Error
- Check Vercel function logs: `vercel logs`
- Verify all environment variables are set
- Check database connection

---

## 📝 Quick Command Reference

```bash
# Pull environment variables
vercel env pull .env.local

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Redeploy
vercel --prod

# Check logs
vercel logs

# View environment variables
vercel env ls
```
















