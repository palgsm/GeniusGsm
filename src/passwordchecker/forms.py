from django import forms

class PasswordCheckForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'أدخل كلمة المرور'}))
