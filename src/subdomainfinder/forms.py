from django import forms
import re


class SubdomainFinderForm(forms.Form):
    """Form for subdomain finder input"""
    
    domain = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'example.com',
            'aria-label': 'Domain name',
            'autocomplete': 'off'
        }),
        label='Domain Name',
        help_text='Enter domain without www (e.g., example.com)'
    )
    
    def clean_domain(self):
        """Validate and clean domain input"""
        domain = self.cleaned_data['domain'].strip().lower()
        
        # Remove common prefixes
        if domain.startswith('http://'):
            domain = domain[7:]
        elif domain.startswith('https://'):
            domain = domain[8:]
        
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Remove trailing slash
        domain = domain.rstrip('/')
        
        # Validate domain format
        domain_pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        if not re.match(domain_pattern, domain):
            raise forms.ValidationError(
                'Invalid domain format. Please enter a valid domain (e.g., example.com)'
            )
        
        if len(domain) < 4:
            raise forms.ValidationError('Domain name is too short')
        
        if len(domain) > 253:
            raise forms.ValidationError('Domain name is too long (max 253 characters)')
        
        return domain
