from django import forms
from .models import AbuseReport


class AbuseReportForm(forms.ModelForm):
    class Meta:
        model = AbuseReport
        fields = ('ip', 'reporter', 'email', 'category', 'description')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
