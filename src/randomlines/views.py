from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
import random


def index(request):
    """Render the Random Lines main page."""
    return render(request, 'randomlines/index.html')


@require_http_methods(['POST'])
def randomize_lines(request):
    """Randomize/shuffle the lines."""
    try:
        data = json.loads(request.body)
        text = data.get('text', '')
        lines = [line for line in text.split('\n')]
        random.shuffle(lines)
        return JsonResponse({'result': '\n'.join(lines)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(['POST'])
def reverse_lines(request):
    """Reverse the order of lines."""
    try:
        data = json.loads(request.body)
        text = data.get('text', '')
        lines = text.split('\n')
        lines.reverse()
        return JsonResponse({'result': '\n'.join(lines)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(['POST'])
def remove_empty(request):
    """Remove empty lines."""
    try:
        data = json.loads(request.body)
        text = data.get('text', '')
        lines = [line for line in text.split('\n') if line.strip()]
        return JsonResponse({'result': '\n'.join(lines)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(['POST'])
def remove_duplicates(request):
    """Remove duplicate lines while preserving order."""
    try:
        data = json.loads(request.body)
        text = data.get('text', '')
        lines = text.split('\n')
        seen = set()
        unique_lines = []
        for line in lines:
            if line not in seen:
                seen.add(line)
                unique_lines.append(line)
        return JsonResponse({'result': '\n'.join(unique_lines)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(['POST'])
def sort_ascending(request):
    """Sort lines in ascending order."""
    try:
        data = json.loads(request.body)
        text = data.get('text', '')
        lines = text.split('\n')
        lines.sort()
        return JsonResponse({'result': '\n'.join(lines)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(['POST'])
def sort_descending(request):
    """Sort lines in descending order."""
    try:
        data = json.loads(request.body)
        text = data.get('text', '')
        lines = text.split('\n')
        lines.sort(reverse=True)
        return JsonResponse({'result': '\n'.join(lines)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
