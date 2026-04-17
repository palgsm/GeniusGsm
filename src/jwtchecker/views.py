import json
import jwt
from datetime import datetime, timezone
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

def index(request):
    return render(request, 'jwtchecker/index.html')

@require_http_methods(["POST"])
def check_jwt(request):
    try:
        data = json.loads(request.body)
        token = data.get('token', '').strip()
        
        if not token:
            return JsonResponse({'error': 'No token provided'}, status=400)
        
        # Decode JWT without verification (to get claims without secret key)
        # In real cases, you might have a secret key
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
        except jwt.InvalidTokenError as e:
            return JsonResponse({'error': f'Invalid JWT token: {str(e)}'}, status=400)
        
        # Get expiry time
        exp_timestamp = decoded.get('exp')
        iat_timestamp = decoded.get('iat')
        
        if not exp_timestamp:
            return JsonResponse({'error': 'Token has no expiry (exp) claim'}, status=400)
        
        # Convert timestamps to datetime
        exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        iat_datetime = datetime.fromtimestamp(iat_timestamp, tz=timezone.utc) if iat_timestamp else None
        
        # Current time
        now = datetime.now(timezone.utc)
        
        # Check if expired
        is_expired = now > exp_datetime
        
        # Calculate time difference
        if is_expired:
            diff = now - exp_datetime
            days = diff.days
            seconds = diff.seconds
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            
            if days > 0:
                time_text = f"Expired {days} day{'s' if days != 1 else ''}, {hours} hour{'s' if hours != 1 else ''} ago"
            elif hours > 0:
                time_text = f"Expired {hours} hour{'s' if hours != 1 else ''}, {minutes} minute{'s' if minutes != 1 else ''} ago"
            else:
                time_text = f"Expired {minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            diff = exp_datetime - now
            days = diff.days
            seconds = diff.seconds
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            
            if days > 0:
                time_text = f"Expires in {days} day{'s' if days != 1 else ''}, {hours} hour{'s' if hours != 1 else ''}"
            elif hours > 0:
                time_text = f"Expires in {hours} hour{'s' if hours != 1 else ''}, {minutes} minute{'s' if minutes != 1 else ''}"
            else:
                time_text = f"Expires in {minutes} minute{'s' if minutes != 1 else ''}"
        
        # Format dates for display
        exp_date_str = exp_datetime.strftime('%m/%d/%Y, %I:%M:%S %p')
        iat_date_str = iat_datetime.strftime('%m/%d/%Y, %I:%M:%S %p') if iat_datetime else 'N/A'
        
        # Get all claims for details display
        claims = {k: v for k, v in decoded.items() if k not in ['exp', 'iat']}
        
        return JsonResponse({
            'status': 'EXPIRED' if is_expired else 'VALID',
            'expiry_date': exp_date_str,
            'issued_at': iat_date_str,
            'time_text': time_text,
            'expiry_timestamp': exp_timestamp,
            'issued_timestamp': iat_timestamp,
            'is_expired': is_expired,
            'all_claims': decoded,
            'other_claims': claims
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid request body'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Error processing token: {str(e)}'}, status=500)
