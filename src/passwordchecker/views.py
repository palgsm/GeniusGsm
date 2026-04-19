import re
import secrets
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from .forms import PasswordCheckForm
from .models import PasswordCheck

def check_password_strength(password):
    score = 0
    feedback = []
    
    if len(password) >= 8:
        score += 1
    else:
        feedback.append('طول قصير (أقل من 8 أحرف)')
    
    if re.search(r'[a-z]', password):
        score += 1
    if re.search(r'[A-Z]', password):
        score += 1
    if re.search(r'\d', password):
        score += 1
    else:
        feedback.append('بدون أرقام')
    
    if re.search(r'[!@#$%^&*]', password):
        score += 1
    else:
        feedback.append('بدون رموز خاصة')
    
    strength = ['ضعيفة جداً', 'ضعيفة', 'متوسطة', 'قوية', 'قوية جداً', 'قوية جداً'][min(score, 5)]
    
    return {'strength': strength, 'score': score, 'feedback': feedback}

@require_http_methods(["GET", "POST"])
def passwordchecker_index(request):
    result = None
    form = PasswordCheckForm()
    
    if request.method == 'POST':
        form = PasswordCheckForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            result = check_password_strength(password)
            PasswordCheck.objects.create(strength=result['strength'])
    
    return render(request, 'passwordchecker/index.html', {'form': form, 'result': result})
