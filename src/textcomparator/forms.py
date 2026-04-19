from django import forms


class TextComparatorForm(forms.Form):
    """Form for comparing texts"""
    
    COMPARISON_TYPES = [
        ('character', 'Character-by-Character'),
        ('word', 'Word-by-Word'),
        ('line', 'Line-by-Line'),
    ]
    
    text1 = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 8,
            'placeholder': 'Enter first text here...',
            'id': 'text1'
        }),
        label='First Text',
        max_length=50000
    )
    
    text2 = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 8,
            'placeholder': 'Enter second text here...',
            'id': 'text2'
        }),
        label='Second Text',
        max_length=50000
    )
    
    comparison_type = forms.ChoiceField(
        choices=COMPARISON_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'comparisonType'
        }),
        label='Comparison Mode'
    )
