from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
import json

from .service import URLAnalyzerService
from .models import URLAnalysisResult


class URLAnalyzerView(TemplateView):
    """Main URL Analyzer view"""
    template_name = 'urlanalyzer/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_analyses'] = URLAnalysisResult.objects.all()[:10]
        return context


class URLAnalyzeAPIView(View):
    """API endpoint for analyzing URLs"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request):
        """Analyze URL via POST request"""
        try:
            data = json.loads(request.body)
            url = data.get('url', '').strip()
            
            if not url:
                return JsonResponse({
                    'success': False,
                    'error': 'URL is required'
                }, status=400)
            
            # Analyze URL
            analysis = URLAnalyzerService.analyze_url(url)
            
            if not analysis.get('is_valid'):
                return JsonResponse({
                    'success': False,
                    'error': analysis.get('error', 'Invalid URL')
                }, status=400)
            
            # Save to database
            expanded_url = analysis.get('expanded_url') or analysis.get('original_url')
            
            result = URLAnalysisResult.objects.create(
                original_url=analysis['original_url'],
                expanded_url=expanded_url if expanded_url != analysis['original_url'] else '',
                domain=analysis['domain'],
                risk_level=analysis['risk_level'],
                is_phishing=analysis['is_phishing'],
                phishing_score=analysis['phishing_score'],
                phishing_indicators=analysis['indicators'],
                has_shortener=analysis['has_shortener'],
                shortener_service=analysis.get('shortener_service', ''),
                has_ssl=analysis['has_ssl'],
                uses_http=not analysis['has_ssl'],
                suspicious_chars=analysis['indicators'].get('suspicious_chars', []),
                title=analysis.get('page_title', ''),
                user_ip=self.get_client_ip(request),
            )
            
            return JsonResponse({
                'success': True,
                'result': {
                    'id': result.id,
                    'original_url': result.original_url,
                    'expanded_url': result.expanded_url or result.original_url,
                    'domain': result.domain,
                    'phishing_score': result.phishing_score,
                    'risk_level': result.risk_level,
                    'is_phishing': result.is_phishing,
                    'has_shortener': result.has_shortener,
                    'shortener_service': result.shortener_service,
                    'has_ssl': result.has_ssl,
                    'indicators': result.phishing_indicators,
                    'page_title': result.title,
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def get(self, request):
        """Get analysis results via GET request"""
        url = request.GET.get('url', '').strip()
        
        if not url:
            return JsonResponse({
                'success': False,
                'error': 'URL parameter is required'
            }, status=400)
        
        # Analyze URL
        analysis = URLAnalyzerService.analyze_url(url)
        
        if not analysis.get('is_valid'):
            return JsonResponse({
                'success': False,
                'error': analysis.get('error', 'Invalid URL')
            }, status=400)
        
        return JsonResponse({
            'success': True,
            'result': {
                'original_url': analysis['original_url'],
                'expanded_url': analysis['expanded_url'],
                'domain': analysis['domain'],
                'phishing_score': analysis['phishing_score'],
                'risk_level': analysis['risk_level'],
                'is_phishing': analysis['is_phishing'],
                'has_shortener': analysis['has_shortener'],
                'shortener_service': analysis.get('shortener_service'),
                'has_ssl': analysis['has_ssl'],
                'indicators': analysis['indicators'],
                'page_title': analysis.get('page_title', ''),
            }
        })
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class URLResultDetailsView(TemplateView):
    """Show detailed analysis results"""
    template_name = 'urlanalyzer/result_details.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        result_id = kwargs.get('result_id')
        
        try:
            result = URLAnalysisResult.objects.get(id=result_id)
            context['result'] = result
            context['risk_color'] = self.get_risk_color(result.risk_level)
        except URLAnalysisResult.DoesNotExist:
            context['error'] = 'Analysis result not found'
        
        return context
    
    @staticmethod
    def get_risk_color(risk_level):
        """Get color for risk level"""
        colors = {
            'safe': '#28a745',      # Green
            'low': '#ffc107',        # Yellow
            'medium': '#fd7e14',     # Orange
            'high': '#dc3545',       # Red
            'critical': '#8b0000',   # Dark Red
        }
        return colors.get(risk_level, '#6c757d')  # Gray

