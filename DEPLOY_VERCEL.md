# 🚀 Deploy Django App to Vercel - Quick Guide

Your TopStyle Business Management System is a **Django-only** application (no React frontend), so we'll deploy it directly to Vercel using serverless functions.

## ✅ Pre-Deployment Checklist

- [x] `vercel.json` created
- [x] `api/index.py` created (serverless entry point)
- [x] Static files collected
- [x] Settings configured for Vercel

## 📋 Step-by-Step Deployment

### Step 1: Complete Vercel Login

1. Open your browser
2. Visit: `https://vercel.com/login`
3. Complete authentication
4. Return to terminal

### Step 2: Deploy to Vercel

Run this command:

```bash
vercel
```

**Or for production:**

```bash
vercel --prod
```

### Step 3: Set Environment Variables

After first deployment, go to Vercel Dashboard → Your Project → Settings → Environment Variables:

**Required Variables:**
```env
SECRET_KEY=your-new-django-secret-key-here
DEBUG=False
ALLOWED_HOSTS=*.vercel.app,your-custom-domain.com
DATABASE_URL=postgresql://user:password@host:port/database
```

**Optional (if using):**
```env
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=your-phone-number
```

### Step 4: Set Up PostgreSQL Database

⚠️ **Important**: SQLite won't work on Vercel. You **must** use PostgreSQL.

**Option A: Vercel Postgres (Easiest)**
1. Go to Vercel Dashboard → Storage → Create Database
2. Select **Postgres**
3. Copy the `DATABASE_URL`
4. Add it to Environment Variables

**Option B: External PostgreSQL**
- [Supabase](https://supabase.com) (Free tier available)
- [Neon](https://neon.tech) (Free tier available)
- [Railway](https://railway.app) (Free tier available)

### Step 5: Run Migrations

After setting up database, you need to run migrations. You can:

1. **Via Vercel CLI:**
```bash
vercel env pull .env.local
python manage.py migrate --settings=topstyle_business.settings
```

2. **Or via Vercel Dashboard:**
   - Use Vercel's console feature (if available)
   - Or set up a one-time migration script

### Step 6: Verify Deployment

1. Visit your Vercel URL: `https://your-project.vercel.app`
2. Test login/registration
3. Check static files are loading
4. Test core functionality

## ⚠️ Important Limitations on Vercel

### 1. Media Files (File Uploads)
- Vercel filesystem is read-only
- File uploads won't persist
- **Solution**: Use external storage:
  - AWS S3
  - Cloudinary
  - Vercel Blob Storage

### 2. Database
- Must use PostgreSQL (SQLite won't work)
- Connection pooling recommended

### 3. Function Timeout
- Free plan: 10 seconds
- Pro plan: 30 seconds (up to 60s)
- Long-running tasks may timeout

### 4. Cold Starts
- First request may take 5-10 seconds
- Subsequent requests are fast

## 🔄 Alternative: Deploy to Render (Recommended for Django)

For a **full-featured Django app** like yours, **Render** is often better:

**Advantages:**
- ✅ Full server environment
- ✅ File uploads work out of the box
- ✅ Easier database setup
- ✅ No cold starts
- ✅ Free tier available
- ✅ Better for business applications

**Deploy to Render:**
1. Go to [render.com](https://render.com)
2. New → Web Service
3. Connect GitHub repo
4. Set build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
5. Set start command: `gunicorn topstyle_business.wsgi`
6. Add environment variables
7. Deploy!

## 📝 Current Vercel Setup

Your project is configured with:
- ✅ `vercel.json` - Routing configuration
- ✅ `api/index.py` - Serverless function entry point
- ✅ Settings updated for Vercel environment
- ✅ Static files collected

## 🚀 Ready to Deploy!

Once you've completed Vercel login in your browser, run:

```bash
vercel --prod
```

This will deploy your Django app to production!
















