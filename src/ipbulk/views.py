from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from .models import IPGroup, IPRange, BulkImportLog
from .forms import IPGroupForm, IPRangeForm, BulkIPImportForm, CheckIPForm, CountryFilterForm, BulkIPLookupForm
import ipaddress
from datetime import datetime
import requests
import json
from geoip2.webservice import Client


class IPGroupListView(ListView):
    """List of IP groups"""
    model = IPGroup
    template_name = 'ipbulk/group_list.html'
    context_object_name = 'groups'
    paginate_by = 20
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add count of ranges and IPs for each group
        for group in context['groups']:
            group.ranges_count = group.ranges.count()
            group.total_ips = group.get_total_ips()
        return context


class IPGroupDetailView(DetailView):
    """IP group details"""
    model = IPGroup
    template_name = 'ipbulk/group_detail.html'
    context_object_name = 'group'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ranges'] = self.object.ranges.all()
        context['total_ips'] = self.object.get_total_ips()
        context['ranges_count'] = self.object.ranges.count()
        return context


class IPGroupCreateView(CreateView):
    """Create new IP group"""
    model = IPGroup
    form_class = IPGroupForm
    template_name = 'ipbulk/group_form.html'
    success_url = reverse_lazy('ipbulk:group_list')
    
    def form_valid(self, form):
        messages.success(self.request, f"Successfully created group '{form.cleaned_data['name']}' successfully")
        return super().form_valid(form)


class IPGroupDeleteView(DeleteView):
    """Delete IP group"""
    model = IPGroup
    template_name = 'ipbulk/group_confirm_delete.html'
    success_url = reverse_lazy('ipbulk:group_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, "Group deleted successfully")
        return super().delete(request, *args, **kwargs)


def bulk_import_view(request):
    """Import IP addresses"""
    if request.method == 'POST':
        form = BulkIPImportForm(request.POST, request.FILES)
        if form.is_valid():
            group = form.cleaned_data['group']
            country = form.cleaned_data['country']
            format_type = form.cleaned_data['format_type']
            
            # Get data
            cidrs, errors = form.get_import_data()
            
            # Create import log
            import_log = BulkImportLog.objects.create(
                file_name=request.FILES.get('file', 'manual_input').name if request.FILES.get('file') else 'manual_input',
                group=group,
                total_records=len(cidrs) + len(errors),
                status='processing'
            )
            
            # Import data
            successful = 0
            failed_items = []
            
            for cidr in cidrs:
                try:
                    IPRange.objects.get_or_create(
                        group=group,
                        cidr=cidr,
                        defaults={'country': country}
                    )
                    successful += 1
                except Exception as e:
                    failed_items.append(f"{cidr}: {str(e)}")
            
            # Add validation errors
            for line_num, line_data, error in errors:
                failed_items.append(f"Line {line_num} ({line_data}): {error}")
            
            # Update log
            import_log.successful_imports = successful
            import_log.failed_imports = len(errors)
            import_log.errors_log = "\n".join(failed_items[:100])  # First 100 errors
            import_log.status = 'completed'
            import_log.completed_at = timezone.now()
            import_log.save()
            
            messages.success(
                request,
                f"Successfully imported {successful} IP ranges out of {import_log.total_records} in country {dict(IPRange.COUNTRY_CHOICES).get(country, 'Unknown')}"
            )
            
            if failed_items:
                messages.warning(
                    request,
                    f"Failed to import {len(failed_items)} ranges. Check format"
                )
            
            return redirect('ipbulk:group_detail', pk=group.pk)
    else:
        form = BulkIPImportForm()
    
    return render(request, 'ipbulk/bulk_import.html', {'form': form})


def check_ip_view(request):
    """Check if IP exists in groups"""
    results = None
    form = CheckIPForm()
    
    if request.method == 'POST':
        form = CheckIPForm(request.POST)
        if form.is_valid():
            ip = form.cleaned_data['ip_address']
            
            results = []
            for group in IPGroup.objects.all():
                for ip_range in group.ranges.all():
                    if ip_range.contains_ip(ip):
                        results.append({
                            'group': group,
                            'range': ip_range,
                            'found': True
                        })
            
            if not results:
                results = []
    
    return render(request, 'ipbulk/check_ip.html', {
        'form': form,
        'results': results
    })


def country_ranges_view(request):
    """Display IP ranges by country"""
    ranges = None
    selected_country = None
    selected_group = None
    ranges_count = 0
    total_ips = 0
    form = CountryFilterForm(request.POST or request.GET)
    
    # Validate data when searching
    if (request.method == 'POST' or request.GET.get('group')) and form.is_valid():
        selected_group = form.cleaned_data.get('group')
        selected_country = form.cleaned_data.get('country')
        
        if selected_group:
            if selected_country:
                # Filter by selected country
                ranges = selected_group.ranges.filter(country=selected_country).order_by('-created_at')
            else:
                # # Show        
                ranges = selected_group.ranges.all().order_by('-created_at')
            
            if ranges:
                ranges_count = ranges.count()
                total_ips = sum(r.get_ip_count() for r in ranges)
    
    return render(request, 'ipbulk/country_ranges.html', {
        'form': form,
        'ranges': ranges,
        'selected_country': selected_country,
        'selected_group': selected_group,
        'ranges_count': ranges_count,
        'total_ips': total_ips,
        'country_choices': IPRange.COUNTRY_CHOICES
    })


def add_ip_range_view(request, group_id):
    """Add a new IP range to group"""
    group = get_object_or_404(IPGroup, pk=group_id)
    
    if request.method == 'POST':
        form = IPRangeForm(request.POST)
        if form.is_valid():
            ip_range = form.save(commit=False)
            ip_range.group = group
            try:
                ip_range.save()
                messages.success(request, f"Range '{ip_range.cidr}' added successfully")
                return redirect('ipbulk:group_detail', pk=group.pk)
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
    else:
        form = IPRangeForm()
    
    return render(request, 'ipbulk/add_range.html', {
        'form': form,
        'group': group
    })


def delete_ip_range_view(request, pk):
    """Delete an IP range"""
    ip_range = get_object_or_404(IPRange, pk=pk)
    group_id = ip_range.group.id
    
    if request.method == 'POST':
        ip_range.delete()
        messages.success(request, "Range deleted successfully")
        return redirect('ipbulk:group_detail', pk=group_id)
    
    return render(request, 'ipbulk/range_confirm_delete.html', {
        'range': ip_range
    })


def get_ip_geolocation(ip_address):
    """
    Get IP location from GeoIP2 API (MaxMind)
    Supports real-time and accurate data
    """
    try:
        # #  GeoIP2 API -    
        # #   ip-api.com 
        response = requests.get(
            f'http://ip-api.com/json/{ip_address}?fields=status,country,countryCode,city,region,isp',
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return {
                    'country': data.get('country', 'Unknown'),
                    'country_code': data.get('countryCode', 'XX'),
                    'city': data.get('city', 'Unknown'),
                    'region': data.get('region', 'Unknown'),
                    'isp': data.get('isp', 'Unknown'),
                    'type': 'API'
                }
    except Exception as e:
        print(f"Error in GeoIP lookup: {e}")
    return None


def bulk_ip_lookup_view(request):
    """Search for multiple IP addresses with geolocation information from GeoIP2""""
    results = None
    found_count = 0
    not_found_count = 0
    success_rate = 0
    form = BulkIPLookupForm()
    
    if request.method == 'POST':
        form = BulkIPLookupForm(request.POST)
        if form.is_valid():
            valid_ips = form.cleaned_data['ip_list']
            results = []
            
            for ip_str in valid_ips:
                ip_result = {
                    'ip': ip_str,
                    'found': False,
                    'country': None,
                    'country_code': None,
                    'city': None,
                    'region': None,
                    'isp': None
                }
                
                # # Search   IP  GeoIP2
                geo_data = get_ip_geolocation(ip_str)
                if geo_data:
                    ip_result['found'] = True
                    ip_result['country'] = geo_data.get('country')
                    ip_result['country_code'] = geo_data.get('country_code')
                    ip_result['city'] = geo_data.get('city')
                    ip_result['region'] = geo_data.get('region')
                    ip_result['isp'] = geo_data.get('isp')
                    found_count += 1
                else:
                    not_found_count += 1
                
                results.append(ip_result)
            
            # #   
            total = len(results)
            if total > 0:
                success_rate = round((found_count / total) * 100)
    
    return render(request, 'ipbulk/bulk_ip_lookup.html', {
        'form': form,
        'results': results,
        'found_count': found_count,
        'not_found_count': not_found_count,
        'success_rate': success_rate
    })
