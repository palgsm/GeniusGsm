import json
import time
import requests
from io import BytesIO
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import SpeedTest


class SpeedTestView(TemplateView):
    """View for Speed Test main page"""
    template_name = 'speedtest/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get recent test results
        context['recent_tests'] = SpeedTest.objects.all()[:10]
        return context


class RealSpeedTestService:
    """Service to perform real internet speed tests with improved accuracy"""
    
    # Test servers for better accuracy
    DOWNLOAD_TEST_URLS = [
        'https://speed.cloudflare.com/__down?bytes=10000000',  # 10MB from Cloudflare
        'https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png',  # Fallback
    ]
    
    @staticmethod
    def test_download_speed():
        """Test download speed with larger file and multiple attempts"""
        try:
            total_bytes = 0
            total_time = 0
            successful_tests = 0
            
            # Try each test URL
            for test_url in RealSpeedTestService.DOWNLOAD_TEST_URLS:
                try:
                    start_time = time.time()
                    response = requests.get(
                        test_url,
                        timeout=15,
                        stream=True,
                        headers={'Connection': 'keep-alive'}
                    )
                    
                    # Calculate bytes downloaded
                    bytes_downloaded = 0
                    for chunk in response.iter_content(chunk_size=65536):
                        if chunk:
                            bytes_downloaded += len(chunk)
                    
                    elapsed_time = time.time() - start_time
                    
                    if bytes_downloaded > 0 and elapsed_time > 0:
                        # Calculate speed in Mbps
                        speed_mbps = (bytes_downloaded * 8) / (elapsed_time * 1_000_000)
                        total_bytes += bytes_downloaded
                        total_time += elapsed_time
                        successful_tests += 1
                        break  # Use first successful test
                except Exception as e:
                    print(f"Download test URL failed ({test_url}): {e}")
                    continue
            
            if successful_tests > 0 and total_time > 0:
                final_speed = (total_bytes * 8) / (total_time * 1_000_000)
                return max(0.05, min(final_speed, 1000))  # Cap at 1000 Mbps
            
            return 0.5  # Fallback if all tests fail
        except Exception as e:
            print(f"Download speed test error: {e}")
            return 0.5
    
    @staticmethod
    def test_upload_speed():
        """Test upload speed with proper timing"""
        try:
            # Test with smaller chunks and proper measurement
            upload_sizes = [512 * 1024, 1024 * 1024]  # 512KB and 1MB
            speeds = []
            
            for upload_size in upload_sizes:
                try:
                    test_data = b'X' * upload_size
                    
                    start_time = time.time()
                    response = requests.post(
                        'https://httpbin.org/post',
                        data=test_data,
                        timeout=15,
                        headers={'Connection': 'keep-alive'}
                    )
                    elapsed_time = time.time() - start_time
                    
                    if response.status_code == 200 and elapsed_time > 0:
                        speed_mbps = (len(test_data) * 8) / (elapsed_time * 1_000_000)
                        speeds.append(speed_mbps)
                except Exception as e:
                    print(f"Upload test size {upload_size} failed: {e}")
                    continue
            
            if speeds:
                # Return average of successful tests
                avg_speed = sum(speeds) / len(speeds)
                return max(0.05, avg_speed)
            
            return 0.5  # Fallback
        except Exception as e:
            print(f"Upload speed test error: {e}")
            return 0.5
    
    @staticmethod
    def test_ping():
        """Test ping latency with multiple servers"""
        try:
            ping_servers = [
                'https://www.google.com',
                'https://www.cloudflare.com',
                'https://www.github.com',
            ]
            
            times = []
            
            for server in ping_servers:
                try:
                    for _ in range(2):  # 2 pings per server
                        start = time.time()
                        response = requests.head(server, timeout=5)
                        elapsed = (time.time() - start) * 1000  # Convert to ms
                        if response.status_code < 400:
                            times.append(elapsed)
                except Exception as e:
                    print(f"Ping to {server} failed: {e}")
                    continue
            
            if times:
                # Return average, excluding outliers
                times.sort()
                # Use median instead of mean for better accuracy
                median_time = times[len(times) // 2]
                return max(1, median_time)
            
            return 10  # Default fallback
        except Exception as e:
            print(f"Ping test error: {e}")
            return 10


@method_decorator(csrf_exempt, name='dispatch')
class SpeedTestAPIView(APIView):
    """API endpoint for performing real speed tests"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            # Check if user provided manual values or wants automatic test
            if 'auto_test' in data and data['auto_test']:
                # Perform real speed test
                service = RealSpeedTestService()
                download_speed = service.test_download_speed()
                upload_speed = service.test_upload_speed()
                ping = service.test_ping()
            else:
                # Use provided values
                download_speed = float(data.get('download_speed', 0))
                upload_speed = float(data.get('upload_speed', 0))
                ping = float(data.get('ping', 0))
            
            # Get IP address
            ip_address = self.get_client_ip(request)
            
            # Determine grade
            if download_speed >= 100:
                grade = 'excellent'
            elif download_speed >= 25:
                grade = 'good'
            elif download_speed >= 5:
                grade = 'fair'
            else:
                grade = 'poor'
            
            # Create record
            test = SpeedTest.objects.create(
                download_speed=download_speed,
                upload_speed=upload_speed,
                ping=ping,
                grade=grade,
                ip_address=ip_address
            )
            
            return Response({
                'success': True,
                'message': 'Speed test result saved successfully',
                'download_speed': round(download_speed, 2),
                'upload_speed': round(upload_speed, 2),
                'ping': round(ping, 2),
                'grade': grade,
                'grade_label': dict(SpeedTest.SPEED_GRADES).get(grade)
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        """Get client's IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


@method_decorator(csrf_exempt, name='dispatch')
class SpeedTestRealizeView(APIView):
    """API endpoint to run real speed test"""
    
    def get(self, request):
        """Perform real speed test"""
        try:
            service = RealSpeedTestService()
            
            download_speed = service.test_download_speed()
            upload_speed = service.test_upload_speed()
            ping = service.test_ping()
            
            # Determine grade
            if download_speed >= 100:
                grade = 'excellent'
            elif download_speed >= 25:
                grade = 'good'
            elif download_speed >= 5:
                grade = 'fair'
            else:
                grade = 'poor'
            
            return Response({
                'download_speed': round(download_speed, 2),
                'upload_speed': round(upload_speed, 2),
                'ping': round(ping, 2),
                'grade': grade,
                'grade_label': dict(SpeedTest.SPEED_GRADES).get(grade),
                'ip': self.get_client_ip(request)
            })
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


@method_decorator(csrf_exempt, name='dispatch')
class SpeedTestUploadView(APIView):
    """API endpoint for upload speed test"""
    
    def post(self, request):
        """Accept upload data"""
        try:
            # Just accept the upload and return success
            return Response({
                'success': True,
                'message': 'Upload test completed'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class SpeedTestDownloadView(APIView):
    """API endpoint for download speed test"""
    
    def post(self, request):
        """Accept download test data"""
        try:
            # Just accept the data and return success
            # This measures the time it takes to send data from client
            return Response({
                'success': True,
                'message': 'Download test completed',
                'bytes_received': len(request.body)
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class SpeedTestPingView(APIView):
    """API endpoint for ping test"""
    
    def get(self, request):
        """Simple ping endpoint"""
        try:
            return Response({
                'success': True,
                'timestamp': time.time()
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)