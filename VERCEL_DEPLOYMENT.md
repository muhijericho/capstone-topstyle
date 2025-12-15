# Deploying TopStyle Business to Vercel

This guide will help you deploy your Django application to Vercel.

## ⚠️ Important Limitations

Before deploying, be aware of Vercel's limitations for Django applications:

1. **Database**: SQLite won't work on Vercel. You **must** use PostgreSQL (recommended) or another external database service.
2. **Media Files**: File uploads won't persist. You need to use external storage like:
   - AWS S3
   - Cloudinary
   - Vercel Blob Storage
3. **Cold Starts**: Serverless functions have cold start delays (first request may be slow).
4. **Function Timeout**: Maximum execution time is 30 seconds (can be extended to 60s on Pro plan).
5. **File System**: Read-only filesystem except `/tmp` directory.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Vercel CLI**: Install globally
   ```bash
   npm install -g vercel
   ```
3. **PostgreSQL Database**: Set up a database (recommended options):
   - [Vercel Postgres](https://vercel.com/docs/storage/vercel-postgres)
   - [Supabase](https://supabase.com)
   - [Neon](https://neon.tech)
   - [Railway](https://railway.app)
   - [Render](https://render.com)

## Step 1: Prepare Your Database

### Option A: Vercel Postgres (Recommended)

1. Go to your Vercel dashboard
2. Navigate to Storage → Create Database → Postgres
3. Copy the connection string

### Option B: External PostgreSQL

Use any PostgreSQL provider and get your connection string.

## Step 2: Configure Environment Variables

Create a `.env` file in your project root (for local testing) and set these in Vercel dashboard:

```env
# Django Settings
SECRET_KEY=your-secret-key-here-generate-a-new-one
DEBUG=False
ALLOWED_HOSTS=your-app.vercel.app,*.vercel.app

# Database (PostgreSQL)
DATABASE_URL=postgresql://user:password@host:port/database

# Email Configuration (if using)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Twilio (if using)
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=your-phone-number
```

**To set in Vercel Dashboard:**
1. Go to your project → Settings → Environment Variables
2. Add each variable for Production, Preview, and Development

## Step 3: Update Settings for Production

The settings are already configured to work with Vercel. Make sure:

- `ALLOWED_HOSTS` includes `*.vercel.app`
- `DEBUG=False` in production
- Database uses `DATABASE_URL` environment variable
- Static files are handled by WhiteNoise

## Step 4: Collect Static Files

Before deploying, collect static files:

```bash
python manage.py collectstatic --noinput
```

This creates the `staticfiles` directory that Vercel will serve.

## Step 5: Run Migrations

Make sure all migrations are created:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Step 6: Deploy to Vercel

### Option A: Using Vercel CLI

1. **Login to Vercel:**
   ```bash
   vercel login
   ```

2. **Deploy:**
   ```bash
   vercel
   ```
   
   Follow the prompts:
   - Set up and deploy? **Yes**
   - Which scope? (Select your account)
   - Link to existing project? **No** (first time) or **Yes** (subsequent)
   - Project name? (Enter a name or press Enter for default)
   - Directory? (Press Enter for current directory)
   - Override settings? **No**

3. **For Production Deployment:**
   ```bash
   vercel --prod
   ```

### Option B: Using GitHub Integration

1. Push your code to GitHub
2. Go to [vercel.com/new](https://vercel.com/new)
3. Import your GitHub repository
4. Configure:
   - Framework Preset: **Other**
   - Root Directory: `.` (root)
   - Build Command: Leave empty (or `python manage.py collectstatic --noinput`)
   - Output Directory: Leave empty
5. Add environment variables
6. Click **Deploy**

## Step 7: Configure Media Files Storage

Since Vercel's filesystem is read-only, you need external storage for media files.

### Option A: Use Django-Storages with AWS S3

1. Install:
   ```bash
   pip install django-storages boto3
   ```

2. Add to `INSTALLED_APPS`:
   ```python
   INSTALLED_APPS = [
       # ... existing apps
       'storages',
   ]
   ```

3. Update settings:
   ```python
   # AWS S3 Settings
   AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='')
   AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='')
   AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='')
   AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
   AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
   AWS_DEFAULT_ACL = 'public-read'
   
   # Use S3 for media files
   DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
   STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
   ```

### Option B: Use Cloudinary

1. Install:
   ```bash
   pip install cloudinary django-cloudinary-storage
   ```

2. Add to `INSTALLED_APPS`:
   ```python
   INSTALLED_APPS = [
       # ... existing apps
       'cloudinary',
       'cloudinary_storage',
   ]
   ```

3. Update settings:
   ```python
   CLOUDINARY_STORAGE = {
       'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME', default=''),
       'API_KEY': config('CLOUDINARY_API_KEY', default=''),
       'API_SECRET': config('CLOUDINARY_API_SECRET', default=''),
   }
   
   DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
   ```

## Step 8: Post-Deployment Checklist

- [ ] Database migrations applied
- [ ] Static files collected and served
- [ ] Environment variables set
- [ ] Media files storage configured
- [ ] Test all major features
- [ ] Check error logs in Vercel dashboard
- [ ] Set up custom domain (optional)

## Troubleshooting

### Static Files Not Loading

1. Make sure `collectstatic` was run
2. Check that `STATIC_ROOT` is set correctly
3. Verify `whitenoise` is in `MIDDLEWARE`

### Database Connection Errors

1. Verify `DATABASE_URL` is set correctly
2. Check database allows connections from Vercel IPs
3. Ensure database is accessible (not behind firewall)

### Media Files Not Working

1. Configure external storage (S3, Cloudinary, etc.)
2. Update `MEDIA_ROOT` and `DEFAULT_FILE_STORAGE` settings
3. Test file uploads after configuration

### Cold Start Issues

- First request may take 5-10 seconds
- Consider using Vercel Pro plan for better performance
- Implement health checks to keep functions warm

### Function Timeout

- Optimize slow queries
- Use database connection pooling
- Consider breaking large operations into smaller tasks

## Additional Resources

- [Vercel Python Documentation](https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python)
- [Django on Vercel Guide](https://vercel.com/guides/deploying-django-to-vercel)
- [Vercel Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)

## Support

If you encounter issues:
1. Check Vercel function logs in dashboard
2. Review Django logs
3. Test locally with `vercel dev`
4. Check Vercel status page

---

**Note**: This deployment setup is optimized for Vercel's serverless platform. For production workloads with high traffic, consider using platforms like Railway, Render, or Heroku that offer traditional server deployments.
















