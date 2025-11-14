"""
Vercel serverless function handler for Django application.
This file wraps the Django WSGI application to work with Vercel's serverless functions.
"""
import os
import sys
import io
from pathlib import Path

# Add the project root to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'review_dashboard.settings')

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application

# Get the WSGI application (cached after first call)
application = get_wsgi_application()

# Vercel serverless function handler
def handler(request):
    """
    Handle incoming requests from Vercel.
    This function adapts Vercel's request format to Django's WSGI format.
    """
    # Extract request information from Vercel request object
    # Vercel Python runtime provides request as an object with these attributes
    method = getattr(request, 'method', 'GET')
    path = getattr(request, 'path', '/')
    headers = dict(getattr(request, 'headers', {}))
    
    # Handle request body
    body = b''
    if hasattr(request, 'body'):
        body = request.body
        if isinstance(body, str):
            body = body.encode('utf-8')
    elif hasattr(request, 'json'):
        import json
        body = json.dumps(request.json).encode('utf-8') if request.json else b''
    
    # Handle query string
    query_string = ''
    if hasattr(request, 'query_string'):
        query_string = request.query_string
    elif hasattr(request, 'query'):
        from urllib.parse import urlencode
        query_string = urlencode(request.query) if request.query else ''
    
    # Create WSGI environment
    host = headers.get('Host', 'localhost')
    server_name = host.split(':')[0] if ':' in host else host
    
    environ = {
        'REQUEST_METHOD': method,
        'PATH_INFO': path,
        'SCRIPT_NAME': '',
        'QUERY_STRING': query_string,
        'CONTENT_TYPE': headers.get('Content-Type', ''),
        'CONTENT_LENGTH': str(len(body)),
        'SERVER_NAME': server_name,
        'SERVER_PORT': headers.get('X-Forwarded-Port', '443'),
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': headers.get('X-Forwarded-Proto', 'https'),
        'wsgi.input': io.BytesIO(body),
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': True,
        'wsgi.run_once': False,
    }
    
    # Add HTTP headers to environ
    for key, value in headers.items():
        key = key.upper().replace('-', '_')
        if key not in ('CONTENT_TYPE', 'CONTENT_LENGTH', 'HOST'):
            environ[f'HTTP_{key}'] = value
    
    # Call Django WSGI application
    status_code = 200
    response_headers = []
    response_body_parts = []
    
    def start_response(status, headers):
        nonlocal status_code, response_headers
        status_code = int(status.split()[0])
        response_headers = headers
    
    # Get response from Django
    try:
        for chunk in application(environ, start_response):
            response_body_parts.append(chunk)
    except Exception as e:
        # Log error and return error response
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/plain'},
            'body': f'Internal Server Error: {str(e)}'
        }
    
    response_body = b''.join(response_body_parts)
    
    # Build response headers dict
    response_headers_dict = dict(response_headers)
    
    # Handle binary content
    try:
        body_text = response_body.decode('utf-8')
    except UnicodeDecodeError:
        # For binary content, return as base64 or handle differently
        import base64
        body_text = base64.b64encode(response_body).decode('utf-8')
        response_headers_dict['Content-Encoding'] = 'base64'
    
    # Return response in Vercel format
    return {
        'statusCode': status_code,
        'headers': response_headers_dict,
        'body': body_text
    }

