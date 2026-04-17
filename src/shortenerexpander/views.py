from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

from .service import ShortenerExpanderService
from .models import ShortenerExpansion


class ShortenerExpanderView(View):
    """Main view for shortener expander UI"""
    
    def get(self, request):
        # Get recent expansions
        recent_expansions = ShortenerExpansion.objects.all()[:10]
        
        context = {
            'recent_expansions': recent_expansions,
        }
        return render(request, 'shortenerexpander/index.html', context)


class ShortenerExpanderAPIView(View):
    """API endpoint for expanding shortened URLs"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        """Expand a shortened URL"""
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST
            
            url = data.get('url', '').strip()
            
            if not url:
                return JsonResponse({
                    'success': False,
                    'error': 'Please provide a URL'
                })
            
            # Expand the URL
            result = ShortenerExpanderService.expand_with_details(url)
            
            # Save to database
            try:
                expansion = ShortenerExpansion.objects.create(
                    original_url=result['original_url'],
                    expanded_url=result['expanded_url'],
                    shortener_service=result.get('shortener_service') or 'unknown',
                    title=result.get('title', ''),
                    is_valid=result.get('is_valid', False),
                    expansion_time_ms=result.get('expansion_time_ms', 0)
                )
                result['id'] = expansion.id
            except Exception as e:
                pass  # Don't fail if we can't save to database
            
            return JsonResponse({
                'success': True,
                'result': result
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    def get(self, request):
        """Get expansion with query parameter"""
        url = request.GET.get('url', '').strip()
        
        if not url:
            return JsonResponse({
                'success': False,
                'error': 'Please provide a URL parameter'
            })
        
        # Expand the URL
        result = ShortenerExpanderService.expand_with_details(url)
        
        # Save to database
        try:
            expansion = ShortenerExpansion.objects.create(
                original_url=result['original_url'],
                expanded_url=result['expanded_url'],
                shortener_service=result.get('shortener_service') or 'unknown',
                title=result.get('title', ''),
                is_valid=result.get('is_valid', False),
                expansion_time_ms=result.get('expansion_time_ms', 0)
            )
            result['id'] = expansion.id
        except Exception as e:
            pass
        
        return JsonResponse({
            'success': True,
            'result': result
        })
