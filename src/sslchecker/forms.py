from django import forms

class SSLCheckForm(forms.Form):
    domain = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter domain name...'}))
