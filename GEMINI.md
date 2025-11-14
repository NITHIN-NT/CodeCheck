# Project Overview

This is a Django-based web application that provides an interactive dashboard for code reviews using the Google Gemini API. Users can paste code snippets into a web interface, and the backend sends the code to the Gemini API for analysis. The results are then displayed in a structured format, highlighting critical issues, best practices, performance concerns, and strengths.

The project uses a standard Django architecture with a single app named `dashboard`. The frontend is built with vanilla JavaScript, HTML, and CSS. The backend uses the `google-generativeai` Python library to communicate with the Gemini API.

# Building and Running

## 1. Install Dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Configure Environment

Create a `.env` file in the project root and add the following variables:

```
DJANGO_SECRET_KEY=<your-secret-key>
GEMINI_API_KEY=<your-gemini-api-key>
```

## 3. Run the Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`.

## 4. Running Tests

```bash
python manage.py test
```

# Development Conventions

*   **Backend:** The backend is a standard Django application. The main logic for interacting with the Gemini API is located in `dashboard/services.py`.
*   **Frontend:** The frontend consists of a single HTML file (`dashboard/templates/dashboard/index.html`) and a JavaScript file (`dashboard/static/dashboard/dashboard.js`).
*   **API:** The application exposes a single API endpoint at `/api/review/` which accepts a POST request with a JSON payload containing the code to be reviewed.
*   **Environment Variables:** The project uses a `.env` file for managing environment variables. A `env.example` file is provided as a template.
*   **Testing:** The project includes a test suite that can be run with `python manage.py test`. The tests stub the Gemini API call to avoid making external requests.
