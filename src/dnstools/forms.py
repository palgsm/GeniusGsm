from django import forms


class DNSQueryForm(forms.Form):
    """Form for DNS queries"""
    domain = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter domain name (e.g., google.com)...',
            'id': 'domainInput'
        }),
        max_length=255
    )
    query_type = forms.ChoiceField(
        choices=[
            ('A', 'A - IPv4 Address'),
            ('AAAA', 'AAAA - IPv6 Address'),
            ('MX', 'MX - Mail Server'),
            ('NS', 'NS - Nameserver'),
            ('SOA', 'SOA - Authority Info'),
            ('CNAME', 'CNAME - Alias'),
            ('TXT', 'TXT - Text Records'),
            ('PTR', 'PTR - Reverse DNS'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'queryType'
        })
    )
