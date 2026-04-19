from django import forms

class EmailCheckForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'أدخل الإيميل'}))
