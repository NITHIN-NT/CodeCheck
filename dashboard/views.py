import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from .services import GeminiAPIError, analyze_code


@ensure_csrf_cookie
def dashboard_view(request):
    return render(request, "dashboard/index.html")


@require_POST
def review_code(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)

    code_snippet = payload.get("code", "").strip()
    if not code_snippet:
        return JsonResponse({"error": "Please paste code to review."}, status=400)

    try:
        review = analyze_code(code_snippet)
    except GeminiAPIError as exc:
        return JsonResponse({"error": str(exc)}, status=502)

    return JsonResponse(review)
