# Vercel Deployment Checklist

## Pre-Deployment

- [ ] Ensure all code is committed to Git
- [ ] Test locally: `python manage.py runserver`
- [ ] Run tests: `python manage.py test`
- [ ] Collect static files: `python manage.py collectstatic --noinput`

## Environment Variables Setup

Set these in Vercel Dashboard → Settings → Environment Variables:

### Required Variables

- [ ] `DJANGO_SECRET_KEY` - Generate with: `python -c "import secrets; print(secrets.token_urlsafe(50))"`
- [ ] `GEMINI_API_KEY` - Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- [ ] `DJANGO_ALLOWED_HOSTS` - Your Vercel domain (e.g., `your-app.vercel.app`)
- [ ] `DEBUG` - Set to `False` for production

### Optional Variables

- [ ] `DJANGO_ALLOWED_HOSTS` - Can include multiple domains separated by commas

## Deployment Methods

### Method 1: Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel

# Deploy to production
vercel --prod
```

### Method 2: GitHub Integration (Recommended)

1. Push code to GitHub
2. Go to [Vercel Dashboard](https://vercel.com/dashboard)
3. Click "Add New Project"
4. Import your repository
5. Configure environment variables
6. Deploy!

## Post-Deployment

- [ ] Verify the site loads: `https://your-app.vercel.app`
- [ ] Test code review functionality
- [ ] Check static files are loading (CSS/JS)
- [ ] Monitor function logs in Vercel Dashboard
- [ ] Test with different code types (Django, React, Node.js)

## Troubleshooting

### Static Files Not Loading
- Check build logs for `collectstatic` output
- Verify `STATIC_ROOT` is set correctly in settings.py
- Check WhiteNoise middleware is enabled

### 500 Errors
- Check Vercel function logs
- Verify all environment variables are set
- Check `ALLOWED_HOSTS` includes your domain

### API Errors
- Verify `GEMINI_API_KEY` is correct
- Check API key has proper permissions
- Review function logs for detailed error messages

## Quick Commands

```bash
# Generate secret key
python -c "import secrets; print(secrets.token_urlsafe(50))"

# Collect static files
python manage.py collectstatic --noinput

# Run tests
python manage.py test

# Local development
python manage.py runserver
```

