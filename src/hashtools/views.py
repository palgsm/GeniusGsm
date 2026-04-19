import hashlib
import base64
import html
import binascii
from urllib.parse import quote, unquote
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import HashHistory, EncodingHistory
from .forms import HashForm, EncodingForm


def perform_hash(input_text, hash_type):
    """Perform hashing operation"""
    try:
        if hash_type == 'md5':
            return hashlib.md5(input_text.encode()).hexdigest()
        elif hash_type == 'sha1':
            return hashlib.sha1(input_text.encode()).hexdigest()
        elif hash_type == 'sha256':
            return hashlib.sha256(input_text.encode()).hexdigest()
        elif hash_type == 'sha512':
            return hashlib.sha512(input_text.encode()).hexdigest()
        elif hash_type == 'blake2':
            return hashlib.blake2b(input_text.encode()).hexdigest()
    except Exception as e:
        return f"Error: {str(e)}"


def perform_encoding(input_text, encoding_type):
    """Perform encoding/decoding operation"""
    try:
        if encoding_type == 'base64_encode':
            return base64.b64encode(input_text.encode()).decode()
        elif encoding_type == 'base64_decode':
            return base64.b64decode(input_text.encode()).decode()
        elif encoding_type == 'url_encode':
            return quote(input_text)
        elif encoding_type == 'url_decode':
            return unquote(input_text)
        elif encoding_type == 'html_encode':
            return html.escape(input_text)
        elif encoding_type == 'html_decode':
            return html.unescape(input_text)
        elif encoding_type == 'hex_encode':
            return input_text.encode().hex()
        elif encoding_type == 'hex_decode':
            return bytes.fromhex(input_text).decode()
    except Exception as e:
        return f"Error: {str(e)}"


@require_http_methods(["GET", "POST"])
def hashtools_index(request):
    """Hash and Encoding tools main view"""
    hash_result = None
    encoding_result = None
    hash_form = HashForm()
    encoding_form = EncodingForm()
    hash_history = HashHistory.objects.all()[:10]
    encoding_history = EncodingHistory.objects.all()[:10]
    
    if request.method == 'POST':
        if 'hash_submit' in request.POST:
            hash_form = HashForm(request.POST)
            if hash_form.is_valid():
                hash_type = hash_form.cleaned_data['hash_type']
                input_text = hash_form.cleaned_data['input_text']
                output = perform_hash(input_text, hash_type)
                hash_result = output
                
                # Save to history
                HashHistory.objects.create(
                    operation_type=hash_type,
                    input_data=input_text[:100],
                    output_data=output
                )
                
        elif 'encoding_submit' in request.POST:
            encoding_form = EncodingForm(request.POST)
            if encoding_form.is_valid():
                encoding_type = encoding_form.cleaned_data['encoding_type']
                input_text = encoding_form.cleaned_data['input_text']
                output = perform_encoding(input_text, encoding_type)
                encoding_result = output
                
                # Save to history
                EncodingHistory.objects.create(
                    encoding_type=encoding_type,
                    input_data=input_text[:100],
                    output_data=output
                )
    
    context = {
        'hash_form': hash_form,
        'encoding_form': encoding_form,
        'hash_result': hash_result,
        'encoding_result': encoding_result,
        'hash_history': hash_history,
        'encoding_history': encoding_history,
        'page_title': 'Hash & Encoding Tools',
        'page_description': 'Tools for hashing text and encoding data (MD5, SHA256, Base64, URL Encoding, etc)',
    }
    
    return render(request, 'hashtools/index.html', context)


@require_http_methods(["POST"])
def api_hash(request):
    """API endpoint for hashing"""
    try:
        hash_type = request.POST.get('hash_type')
        input_text = request.POST.get('input_text')
        
        if not hash_type or not input_text:
            return JsonResponse({'error': 'Missing parameters'}, status=400)
        
        result = perform_hash(input_text, hash_type)
        
        # Save to history
        HashHistory.objects.create(
            operation_type=hash_type,
            input_data=input_text[:100],
            output_data=result
        )
        
        return JsonResponse({
            'success': True,
            'hash_type': hash_type,
            'result': result
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["POST"])
def api_encode(request):
    """API endpoint for encoding"""
    try:
        encoding_type = request.POST.get('encoding_type')
        input_text = request.POST.get('input_text')
        
        if not encoding_type or not input_text:
            return JsonResponse({'error': 'Missing parameters'}, status=400)
        
        result = perform_encoding(input_text, encoding_type)
        
        # Save to history
        EncodingHistory.objects.create(
            encoding_type=encoding_type,
            input_data=input_text[:100],
            output_data=result
        )
        
        return JsonResponse({
            'success': True,
            'encoding_type': encoding_type,
            'result': result
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
