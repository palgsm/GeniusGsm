from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

from .service import PhishingDetectorService
from .models import PhishingDetection


class PhishingDetectorView(View):
    """Main view for phishing detector UI"""
    
    def get(self, request):
        recent_detections = PhishingDetection.objects.all()[:10]
        context = {'recent_detections': recent_detections}
        return render(request, 'phishingdetector/index.html', context)


class PhishingDetectorAPIView(View):
    """API endpoint for phishing detection"""
    
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
            
            # Detect phishing
            result = PhishingDetectorService.detect_phishing(url)
            
            # Save to database
            try:
                detection = PhishingDetection.objects.create(
                    url=result['url'],
                    domain=result['domain'],
                    phishing_score=result['phishing_score'],
                    risk_level=result['risk_level'],
                    is_phishing=result['is_phishing'],
                    form_fields=result['form_fields'],
                    page_title=result['page_title'],
                    indicators_found=json.dumps(result['indicators']),
                    detection_method=result['method']
                )
                result['id'] = detection.id
            except Exception as e:
                pass
            
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
        url = request.GET.get('url', '').strip()
        
        if not url:
            return JsonResponse({
                'success': False,
                'error': 'Please provide a URL parameter'
            })
        
        result = PhishingDetectorService.detect_phishing(url)
        
        try:
            detection = PhishingDetection.objects.create(
                url=result['url'],
                domain=result['domain'],
                phishing_score=result['phishing_score'],
                risk_level=result['risk_level'],
                is_phishing=result['is_phishing'],
                form_fields=result['form_fields'],
                page_title=result['page_title'],
                indicators_found=json.dumps(result['indicators']),
                detection_method=result['method']
            )
            result['id'] = detection.id
        except Exception as e:
            pass
        
        return JsonResponse({
            'success': True,
            'result': result
        })
