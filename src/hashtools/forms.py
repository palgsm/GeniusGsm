from django import forms


class HashForm(forms.Form):
    """Form for hashing operations"""
    hash_type = forms.ChoiceField(
        choices=[
            ('md5', 'MD5'),
            ('sha1', 'SHA-1'),
            ('sha256', 'SHA-256'),
            ('sha512', 'SHA-512'),
            ('blake2', 'BLAKE2'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'hashType'
        })
    )
    input_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'أدخل النص للتجزئة...',
            'id': 'inputText'
        }),
        max_length=5000
    )


class EncodingForm(forms.Form):
    """Form for encoding/decoding operations"""
    encoding_type = forms.ChoiceField(
        choices=[
            ('base64_encode', 'Base64 Encode'),
            ('base64_decode', 'Base64 Decode'),
            ('url_encode', 'URL Encode'),
            ('url_decode', 'URL Decode'),
            ('html_encode', 'HTML Encode'),
            ('html_decode', 'HTML Decode'),
            ('hex_encode', 'Hex Encode'),
            ('hex_decode', 'Hex Decode'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'encodingType'
        })
    )
    input_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'أدخل النص للترميز...',
            'id': 'inputText2'
        }),
        max_length=5000
    )
