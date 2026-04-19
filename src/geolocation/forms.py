from django import forms

class GeolocationForm(forms.Form):
    ip_address = forms.GenericIPAddressField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'أدخل عنوان IP'}))
