from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

from .service import LinkPreviewService
from .models import LinkPreview


class LinkPreviewView(View):
    """Main view for link preview UI"""
    
    def get(self, request):
        recent_previews = LinkPreview.objects.all()[:10]
        context = {'recent_previews': recent_previews}
        return render(request, 'linkpreview/index.html', context)


class LinkPreviewAPIView(View):
    """API endpoint for generating link previews"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
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
            
            # Check if preview already exists
            existing = LinkPreview.objects.filter(url=url).first()
            if existing:
                existing.view_count += 1
                existing.save(update_fields=['view_count', 'last_accessed'])
                preview_data = LinkPreviewService.get_preview_summary({
                    'url': existing.url,
                    'title': existing.title,
                    'description': existing.description,
                    'image_url': existing.image_url,
                    'favicon_url': existing.favicon_url,
                    'domain': existing.domain,
                    'page_size': existing.page_size,
                    'load_time': existing.load_time,
                    'content_type': existing.content_type,
                    'og_data': existing.get_og_data(),
                    'twitter_data': existing.get_twitter_data(),
                    'dominant_color': existing.dominant_color,
                    'is_valid': existing.is_valid,
                    'error': existing.error_message
                })
                preview_data['id'] = existing.id
                preview_data['cached'] = True
                
                return JsonResponse({
                    'success': True,
                    'result': preview_data
                })
            
            # Generate new preview
            result = LinkPreviewService.generate_preview(url)
            
            # Save to database
            try:
                preview = LinkPreview.objects.create(
                    url=result.get('url', url),
                    title=result.get('title', '')[:500] if result.get('title') else '',
                    description=result.get('description', '') if result.get('description') else '',
                    image_url=result.get('image_url', ''),
                    favicon_url=result.get('favicon_url', ''),
                    domain=result.get('domain', ''),
                    page_size=result.get('page_size'),
                    load_time=result.get('load_time'),
                    content_type=result.get('content_type'),
                    og_data=json.dumps(result.get('og_data', {})),
                    twitter_data=json.dumps(result.get('twitter_data', {})),
                    dominant_color=result.get('dominant_color', '#3498db'),
                    is_valid=result.get('is_valid', False),
                    error_message=result.get('error', '')
                )
                result['id'] = preview.id
            except Exception as e:
                pass
            
            preview_data = LinkPreviewService.get_preview_summary(result)
            
            return JsonResponse({
                'success': result.get('success', False),
                'result': preview_data
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    def get(self, request):
        url = request.GET.get('url', '').strip()
        
        if not url:
            return JsonResponse({
                'success': False,
                'error': 'Please provide a URL parameter'
            })
        
        result = LinkPreviewService.generate_preview(url)
        
        try:
            preview = LinkPreview.objects.create(
                url=result.get('url', url),
                title=result.get('title', '')[:500] if result.get('title') else '',
                description=result.get('description', '') if result.get('description') else '',
                image_url=result.get('image_url', ''),
                favicon_url=result.get('favicon_url', ''),
                domain=result.get('domain', ''),
                page_size=result.get('page_size'),
                load_time=result.get('load_time'),
                content_type=result.get('content_type'),
                og_data=json.dumps(result.get('og_data', {})),
                twitter_data=json.dumps(result.get('twitter_data', {})),
                dominant_color=result.get('dominant_color', '#3498db'),
                is_valid=result.get('is_valid', False),
                error_message=result.get('error', '')
            )
            result['id'] = preview.id
        except Exception as e:
            pass
        
        preview_data = LinkPreviewService.get_preview_summary(result)
        
        return JsonResponse({
            'success': result.get('success', False),
            'result': preview_data
        })
