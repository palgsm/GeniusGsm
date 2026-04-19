from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import difflib
from .models import TextComparison
from .forms import TextComparatorForm


def calculate_similarity(text1, text2):
    """Calculate similarity percentage between two texts"""
    matcher = difflib.SequenceMatcher(None, text1, text2)
    return matcher.ratio() * 100


def perform_comparison(text1, text2, comparison_type):
    """Perform different types of text comparison"""
    
    results = []
    
    if comparison_type == 'character':
        # Character-by-character comparison
        diff = difflib.unified_diff(
            text1.splitlines(keepends=True),
            text2.splitlines(keepends=True),
            fromfile='Text 1',
            tofile='Text 2',
            lineterm=''
        )
        results = list(diff)
        
    elif comparison_type == 'word':
        # Word-by-word comparison
        words1 = text1.split()
        words2 = text2.split()
        
        diff = difflib.unified_diff(
            words1,
            words2,
            fromfile='Text 1',
            tofile='Text 2',
            lineterm=''
        )
        results = list(diff)
        
    elif comparison_type == 'line':
        # Line-by-line comparison
        lines1 = text1.splitlines()
        lines2 = text2.splitlines()
        
        diff = difflib.unified_diff(
            lines1,
            lines2,
            fromfile='Text 1',
            tofile='Text 2',
            lineterm=''
        )
        results = list(diff)
    
    # Count differences
    differences = sum(1 for line in results if line.startswith(('+', '-')) and not line.startswith(('+++', '---')))
    
    return results, differences


@require_http_methods(["GET", "POST"])
def textcomparator_view(request):
    """Main text comparator view"""
    
    form = TextComparatorForm()
    comparison_result = None
    similarity = None
    history = TextComparison.objects.all()[:10]
    
    if request.method == 'POST':
        form = TextComparatorForm(request.POST)
        
        if form.is_valid():
            text1 = form.cleaned_data['text1']
            text2 = form.cleaned_data['text2']
            comparison_type = form.cleaned_data['comparison_type']
            
            # Perform comparison
            diff_result, differences = perform_comparison(text1, text2, comparison_type)
            similarity = calculate_similarity(text1, text2)
            
            # Store comparison
            TextComparison.objects.create(
                text1=text1[:500],  # Store first 500 chars for history
                text2=text2[:500],
                comparison_type=comparison_type,
                similarity_percentage=similarity,
                differences_count=differences
            )
            
            comparison_result = {
                'text1': text1,
                'text2': text2,
                'type': comparison_type,
                'diff': '\n'.join(diff_result),
                'differences': differences,
                'similarity': round(similarity, 2)
            }
            
            # Refresh history
            history = TextComparison.objects.all()[:10]
    
    context = {
        'form': form,
        'comparison_result': comparison_result,
        'similarity': similarity,
        'history': history,
        'page_title': 'Text & File Comparator',
        'page_description': 'Compare texts and files to find differences - character, word, and line-by-line comparison'
    }
    
    return render(request, 'textcomparator/index.html', context)


@require_http_methods(["POST"])
def api_compare(request):
    """API endpoint for text comparison"""
    try:
        text1 = request.POST.get('text1', '')
        text2 = request.POST.get('text2', '')
        comparison_type = request.POST.get('type', 'character')
        
        if not text1 or not text2:
            return JsonResponse({'error': 'Both texts are required'}, status=400)
        
        diff_result, differences = perform_comparison(text1, text2, comparison_type)
        similarity = calculate_similarity(text1, text2)
        
        TextComparison.objects.create(
            text1=text1[:500],
            text2=text2[:500],
            comparison_type=comparison_type,
            similarity_percentage=similarity,
            differences_count=differences
        )
        
        return JsonResponse({
            'success': True,
            'differences': differences,
            'similarity': round(similarity, 2),
            'diff': '\n'.join(diff_result[:100])  # Limit to first 100 lines
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
