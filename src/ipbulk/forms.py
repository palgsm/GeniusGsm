from django import forms
from .models import IPGroup, IPRange, BulkImportLog
import ipaddress
from django.core.exceptions import ValidationError


class IPGroupForm(forms.ModelForm):
    class Meta:
        model = IPGroup
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Group Name (e.g., VPN Ranges, Datacenter IPs)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Group Description (optional)'
            })
        }


class IPRangeForm(forms.ModelForm):
    class Meta:
        model = IPRange
        fields = ['cidr', 'country', 'description']
        widgets = {
            'cidr': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter CIDR notation (e.g., 192.168.0.0/24 or 10.0.0.0/8)'
            }),
            'country': forms.Select(attrs={
                'class': 'form-control',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Range Description (optional)'
            })
        }


class BulkIPImportForm(forms.Form):
    """Form for bulk batch IP import from file"""
    group = forms.ModelChoiceField(
        queryset=IPGroup.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Select Group"
    )
    
    country = forms.ChoiceField(
        choices=IPRange.COUNTRY_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Select Country"
    )
    
    IMPORT_FORMAT_CHOICES = [
        ('cidr', 'CIDR Format (192.168.0.0/24)'),
        ('range', 'Range Format (192.168.0.0 - 192.168.0.255)'),
        ('single', 'Single IPs (one per line)'),
    ]
    format_type = forms.ChoiceField(
        choices=IMPORT_FORMAT_CHOICES,
        required=True,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label="Import Format"
    )
    
    file = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.txt,.csv'
        }),
        label="Upload File (txt, csv)"
    )
    
    text_input = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 10,
            'placeholder': 'Or paste the list here (one IP/CIDR per line)'
        }),
        label="Or Enter Data Directly"
    )
    
    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        text_input = cleaned_data.get('text_input')
        
        if not file and not text_input:
            raise ValidationError("You must upload a file or enter data directly")
        
        return cleaned_data
    
    def get_import_data(self):
        """Extract data from file or text"""
        file = self.cleaned_data.get('file')
        text_input = self.cleaned_data.get('text_input')
        format_type = self.cleaned_data.get('format_type')
        
        lines = []
        
        if file:
            try:
                content = file.read().decode('utf-8')
                lines = [line.strip() for line in content.split('\n') if line.strip()]
            except Exception as e:
                raise ValidationError(f"Error reading file: {str(e)}")
        
        if text_input:
            lines.extend([line.strip() for line in text_input.split('\n') if line.strip()])
        
        # Convert data by format
        cidrs = []
        errors = []
        
        for i, line in enumerate(lines, 1):
            # Clean line
            line = line.strip().split('#')[0].strip()  # Remove comments
            if not line:
                continue
            
            try:
                if format_type == 'cidr':
                    # Verify CIDR directly
                    network = ipaddress.ip_network(line, strict=False)
                    cidrs.append(str(network))
                
                elif format_type == 'range':
                    # Convert Range to CIDR
                    parts = line.split('-')
                    if len(parts) != 2:
                        raise ValueError("Format should be: IP1 - IP2")
                    start_ip = ipaddress.ip_address(parts[0].strip())
                    end_ip = ipaddress.ip_address(parts[1].strip())
                    
                    # Convert range to CIDR (approximate)
                    cidrs.append(f"{start_ip}/32") if start_ip == end_ip else cidrs.append(line)
                
                elif format_type == 'single':
                    # Check single IP
                    ip = ipaddress.ip_address(line)
                    if ip.version == 4:
                        cidrs.append(f"{line}/32")
                    else:
                        cidrs.append(f"{line}/128")
            
            except ValueError as e:
                errors.append((i, line, str(e)))
        
        return cidrs, errors


class CheckIPForm(forms.Form):
    """Form to check if IP exists in groups"""
    ip_address = forms.CharField(
        max_length=45,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter IP address to check'
        }),
        label="IP Address"
    )
    
    def clean_ip_address(self):
        ip = self.cleaned_data['ip_address']
        try:
            ipaddress.ip_address(ip)
        except ValueError:
            raise ValidationError("Invalid IP address")
        return ip


class CountryFilterForm(forms.Form):
    """Form to filter ranges by countries"""
    group = forms.ModelChoiceField(
        queryset=IPGroup.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Select Group"
    )
    
    country = forms.ChoiceField(
        choices=[('', '-- All Countries --')] + IPRange.COUNTRY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Select Country"
    )


class BulkIPLookupForm(forms.Form):
    """Form for searching multiple IPs"""
    ip_list = forms.CharField(
        label="IP Addresses List",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 10,
            'placeholder': 'Enter IP addresses one per line (max 100)\nExample:\n8.8.8.8\n1.1.1.1\n192.168.1.1'
        }),
        help_text="Enter IP addresses one per line (max 100)"
    )
    
    def clean_ip_list(self):
        ip_list = self.cleaned_data['ip_list']
        lines = [line.strip() for line in ip_list.split('\n') if line.strip()]
        
        if len(lines) > 100:
            raise ValidationError("Maximum 100 IP addresses")
        
        if not lines:
            raise ValidationError("Enter at least one IP address")
        
        valid_ips = []
        errors = []
        
        for i, line in enumerate(lines, 1):
            try:
                ip = ipaddress.ip_address(line)
                valid_ips.append(str(ip))
            except ValueError:
                errors.append(f"Line {i}: {line} (invalid IP address)")
        
        if errors:
            error_msg = "\n".join(errors[:5])
            if len(errors) > 5:
                error_msg += f"\n... and {len(errors) - 5} more errors"
            raise ValidationError(f"Text errors:\n{error_msg}")
        
        return valid_ips
