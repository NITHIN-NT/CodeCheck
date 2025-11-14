# Django Code Review Dashboard

Interactive dashboard for consolidating AI-powered code reviews. Paste any code snippet, send it to Gemini via a Django backend, and receive a structured summary highlighting critical blockers, best-practice gaps, performance concerns, and strengths.

## Tech Stack

- Django 5
- HTML + CSS + vanilla JavaScript
- Google Gemini API (`google-generativeai`)
- `python-dotenv` for environment management

## Getting Started

1. **Install dependencies**

   ```bash
   cd /Users/nithinraj/Desktop/Project/tester
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure environment**

   ```bash
   cp env.example .env
   # edit .env to add secure values
   ```

   Required keys:

   - `DJANGO_SECRET_KEY` – any random string for local dev.
   - `GEMINI_API_KEY` – Google AI Studio key used for code reviews.

3. **Run the server**

   ```bash
   source .venv/bin/activate
   python manage.py runserver
   ```

   Open `http://127.0.0.1:8000/` to use the dashboard.

## How It Works

- The dashboard loads from `dashboard/templates/dashboard/index.html`.
- JavaScript (`dashboard/static/dashboard/dashboard.js`) submits the pasted code to `/api/review/`.
- `dashboard.services.analyze_code` sends the prompt + code to Gemini and normalizes the JSON response for the UI.
- The UI updates metric counts and sections (Critical, Best Practices, Performance, Strengths) in real-time.

## Testing

```bash
source .venv/bin/activate
python manage.py test
```

Tests stub the Gemini call so no external requests are made.

## Deployment to Vercel

This project is configured for deployment on Vercel using serverless functions.

### Prerequisites

1. Install Vercel CLI (optional, for local testing):
   ```bash
   npm i -g vercel
   ```

2. Create a Vercel account at [vercel.com](https://vercel.com)

### Quick Deployment Steps

1. **Install Vercel CLI and login:**
   ```bash
   npm i -g vercel
   vercel login
   ```

2. **Deploy from project directory:**
   ```bash
   vercel
   ```
   Follow the prompts to link your project.

3. **Set Environment Variables:**
   After first deployment, go to your project settings in Vercel Dashboard:
   - Navigate to Settings → Environment Variables
   - Add the following:
     - `DJANGO_SECRET_KEY` - Generate a secure random string (you can use: `python -c "import secrets; print(secrets.token_urlsafe(50))"`)
     - `GEMINI_API_KEY` - Your Google Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
     - `DJANGO_ALLOWED_HOSTS` - Your Vercel domain (e.g., `your-app.vercel.app,your-custom-domain.com`)
     - `DEBUG` - Set to `False` for production

4. **Redeploy:**
   ```bash
   vercel --prod
   ```
   Or push to your connected Git repository for automatic deployment.

### GitHub Integration (Recommended)

1. Push your code to GitHub
2. Go to [Vercel Dashboard](https://vercel.com/dashboard)
3. Click "Add New Project"
4. Import your GitHub repository
5. Configure environment variables in project settings
6. Deploy!

### Project Structure for Vercel

- `vercel.json` - Vercel configuration file
- `api/index.py` - Serverless function handler that wraps Django WSGI application
- `.vercelignore` - Files to exclude from deployment
- Static files are handled by WhiteNoise middleware

### Important Notes

- **Function Timeout**: The serverless function has a 30-second timeout (configurable in `vercel.json`)
- **Memory**: Allocated 1024MB memory for the function
- **Static Files**: Handled by WhiteNoise middleware, automatically collected during build
- **Database**: SQLite is used by default. For production with persistent data, consider:
  - Vercel Postgres
  - PlanetScale
  - Supabase
  - Other managed database services
- **Environment Variables**: Must be set in Vercel Dashboard for production
- **Code Detection**: The Django app automatically detects code type (Django, React, Node.js, etc.) and adapts the review accordingly

### Troubleshooting

- **Static files not loading**: Ensure `collectstatic` runs during build (configured in `vercel.json`)
- **500 errors**: Check Vercel function logs in the dashboard
- **API key errors**: Verify `GEMINI_API_KEY` is set correctly in environment variables
- **CORS issues**: Check `ALLOWED_HOSTS` includes your Vercel domain

## Notes

- The Gemini API key is loaded at runtime; without it, the API endpoint returns a helpful error message.
- Static assets live under `dashboard/static/dashboard/` so they ship with Django's default static files pipeline.

