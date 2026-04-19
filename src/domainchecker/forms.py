from django import forms


class DomainCheckForm(forms.Form):
    domain = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter domain name (e.g., google.com)...',',
        }),
        max_length=255
    )
