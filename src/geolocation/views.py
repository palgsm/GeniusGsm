import geoip2.database
import os
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from .forms import GeolocationForm
from .models import IPGeolocation

geoip_reader = None
try:
    possible = ['/usr/share/GeoIP/GeoLite2-City.mmdb']
    for p in possible:
        if os.path.exists(p):
            geoip_reader = geoip2.database.Reader(p)
            break
except:
    pass

@require_http_methods(["GET", "POST"])
def geolocation_index(request):
    result = None
    form = GeolocationForm()
    
    if request.method == 'POST':
        form = GeolocationForm(request.POST)
        if form.is_valid():
            ip = form.cleaned_data['ip_address']
            try:
                if geoip_reader:
                    response = geoip_reader.city(ip)
                    result = {
                        'country': response.country.name,
                        'city': response.city.name,
                        'latitude': response.location.latitude,
                        'longitude': response.location.longitude,
                    }
                    IPGeolocation.objects.create(ip_address=ip, country=response.country.name, city=response.city.name)
                else:
                    result = {'error': 'GeoIP database not available'}
            except Exception as e:
                result = {'error': str(e)}
    
    return render(request, 'geolocation/index.html', {'form': form, 'result': result})
