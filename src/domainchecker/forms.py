from django import forms


class DomainCheckForm(forms.Form):
    domain = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل اسم الدومين (مثال: google.com)',
        }),
        max_length=255
    )
