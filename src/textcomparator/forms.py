from django import forms


class TextComparatorForm(forms.Form):
    """Form for comparing texts and files"""
    
    COMPARISON_TYPES = [
        ('character', 'Character-by-Character'),
        ('word', 'Word-by-Word'),
        ('line', 'Line-by-Line'),
    ]
    
    INPUT_TYPES = [
        ('text', 'Text Input'),
        ('file', 'File Upload'),
        ('multi', 'Multiple Files (1 vs Many)'),
    ]
    
    # Input type selector
    input_type = forms.ChoiceField(
        choices=INPUT_TYPES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input',
            'id': 'inputType',
            'onchange': 'toggleInputType()'
        }),
        label='Choose Input Type',
        initial='text',
        required=False
    )
    
    # Text inputs
    text1 = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 8,
            'placeholder': 'Enter first text here...',
            'id': 'text1'
        }),
        label='First Text',
        max_length=50000,
        required=False
    )
    
    text2 = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 8,
            'placeholder': 'Enter second text here...',
            'id': 'text2'
        }),
        label='Second Text',
        max_length=50000,
        required=False
    )
    
    # File uploads (support .txt, .py, .js, .json, .csv, .xml, etc)
    file1 = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'id': 'file1',
            'accept': '.txt,.py,.js,.json,.csv,.xml,.html,.css,.md,.log',
            'style': 'display:none;'
        }),
        label='First File',
        required=False
    )
    
    file2 = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'id': 'file2',
            'accept': '.txt,.py,.js,.json,.csv,.xml,.html,.css,.md,.log',
            'style': 'display:none;'
        }),
        label='Second File',
        required=False
    )
    
    # Multiple file uploads (note: compare_files will be handled specially in views)
    base_file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'id': 'baseFile',
            'accept': '.txt,.py,.js,.json,.csv,.xml,.html,.css,.md,.log',
            'style': 'display:none;'
        }),
        label='Base File (One)',
        required=False
    )
    
    comparison_type = forms.ChoiceField(
        choices=COMPARISON_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'comparisonType'
        }),
        label='Comparison Mode'
    )


