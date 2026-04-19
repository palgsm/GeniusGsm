from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
import difflib
import json
from .models import TextComparison, MultiFileComparison
from .forms import TextComparatorForm
from datetime import datetime


def calculate_similarity(text1, text2):
    """Calculate similarity percentage between two texts"""
    matcher = difflib.SequenceMatcher(None, text1, text2)
    return matcher.ratio() * 100


def perform_similarities_differences_comparison(text1, text2):
    """
    Compare texts and separate similarities from differences
    Returns: (similarities_list, differences_list)
    """
    lines1 = text1.splitlines()
    lines2 = text2.splitlines()
    
    matcher = difflib.SequenceMatcher(None, lines1, lines2)
    matching_blocks = matcher.get_matching_blocks()
    
    similarities = []
    differences_removed = []
    differences_added = []
    
    # Collect matching blocks
    for block in matching_blocks:
        if block.size > 0:
            for i in range(block.size):
                similarities.append(lines1[block.a + i])
    
    # Collect differences using unified_diff
    diff = difflib.unified_diff(
        lines1,
        lines2,
        fromfile='Text 1 (Removed)',
        tofile='Text 2 (Added)',
        lineterm=''
    )
    
    for line in diff:
        if line.startswith('-') and not line.startswith('---'):
            differences_removed.append(line[1:])
        elif line.startswith('+') and not line.startswith('+++'):
            differences_added.append(line[1:])
    
    return similarities, differences_removed, differences_added


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
    
    elif comparison_type == 'similarities_differences':
        # Similarities and Differences separated comparison
        similarities, differences_removed, differences_added = perform_similarities_differences_comparison(text1, text2)
        results = {
            'similarities': similarities,
            'removed': differences_removed,
            'added': differences_added
        }
        # Return early for this type
        differences = len(differences_removed) + len(differences_added)
        return results, differences
    
    # Count differences
    differences = sum(1 for line in results if line.startswith(('+', '-')) and not line.startswith(('+++', '---')))
    
    return results, differences


def perform_multi_comparison(base_content, base_filename, compare_files_data, comparison_type):
    """
    Perform comparison of one base file with multiple files
    
    Returns:
        - similarity_data: dict with filename -> similarity percentage
        - detailed_comparisons: dict with filename -> diff output
    """
    similarity_data = {}
    detailed_comparisons = {}
    
    for filename, content in compare_files_data.items():
        similarity = calculate_similarity(base_content, content)
        diff, _ = perform_comparison(base_content, content, comparison_type)
        
        similarity_data[filename] = round(similarity, 2)
        detailed_comparisons[filename] = '\n'.join(diff)
    
    return similarity_data, detailed_comparisons


@require_http_methods(["GET", "POST"])
def textcomparator_view(request):
    """Main text comparator view - supports text, dual files, and multi-file comparisons"""
    
    form = TextComparatorForm()
    comparison_result = None
    similarity = None
    history = TextComparison.objects.all()[:10]
    
    if request.method == 'POST':
        form = TextComparatorForm(request.POST, request.FILES)
        
        if form.is_valid():
            input_type = request.POST.get('input_type', 'text')
            comparison_type = form.cleaned_data['comparison_type']
            
            # Get text content based on input type
            if input_type == 'multi':
                # Handle multi-file comparison (1 base file vs multiple comparison files)
                base_file = request.FILES.get('base_file')
                compare_files = request.FILES.getlist('compare_files')
                
                if not base_file or not compare_files:
                    form.add_error(None, "Base file and at least one comparison file are required")
                    context = {
                        'form': form,
                        'comparison_result': None,
                        'similarity': None,
                        'history': history,
                        'page_title': 'Text & File Comparator',
                        'page_description': 'Compare texts and files to find differences'
                    }
                    return render(request, 'textcomparator/index.html', context)
                
                try:
                    # Read base file
                    if base_file.size > 1048576:
                        form.add_error(None, "Base file size must be less than 1MB")
                        context = {
                            'form': form,
                            'comparison_result': None,
                            'similarity': None,
                            'history': history,
                            'page_title': 'Text & File Comparator',
                            'page_description': 'Compare texts and files to find differences'
                        }
                        return render(request, 'textcomparator/index.html', context)
                    
                    base_content = base_file.read().decode('utf-8', errors='replace')
                    base_file_name = base_file.name
                    
                    # Read comparison files
                    compare_files_data = {}
                    comparison_file_names = []
                    
                    for compare_file in compare_files:
                        if compare_file.size > 1048576:
                            form.add_error(None, f"File '{compare_file.name}' exceeds 1MB limit")
                            context = {
                                'form': form,
                                'comparison_result': None,
                                'similarity': None,
                                'history': history,
                                'page_title': 'Text & File Comparator',
                                'page_description': 'Compare texts and files to find differences'
                            }
                            return render(request, 'textcomparator/index.html', context)
                        
                        file_content = compare_file.read().decode('utf-8', errors='replace')
                        compare_files_data[compare_file.name] = file_content
                        comparison_file_names.append(compare_file.name)
                    
                    # Perform multi-file comparison
                    similarity_data, detailed_comparisons = perform_multi_comparison(
                        base_content, base_file_name, compare_files_data, comparison_type
                    )
                    
                    # Store multi-file comparison
                    MultiFileComparison.objects.create(
                        base_file_name=base_file_name,
                        comparison_file_names=', '.join(comparison_file_names),
                        comparison_type=comparison_type,
                        total_files=len(compare_files) + 1,
                        similarity_data=similarity_data
                    )
                    
                    comparison_result = {
                        'mode': 'multi',
                        'base_file_name': base_file_name,
                        'comparison_files': comparison_file_names,
                        'comparison_type': comparison_type,
                        'similarity_data': similarity_data,
                        'detailed_comparisons': detailed_comparisons,
                        'total_files': len(compare_files) + 1
                    }
                    
                except Exception as e:
                    form.add_error(None, f"Error processing files: {str(e)}")
                    context = {
                        'form': form,
                        'comparison_result': None,
                        'similarity': None,
                        'history': history,
                        'page_title': 'Text & File Comparator',
                        'page_description': 'Compare texts and files to find differences'
                    }
                    return render(request, 'textcomparator/index.html', context)
                
                # Refresh history
                history = TextComparison.objects.all()[:10]
            
            elif input_type == 'file':
                # Read from uploaded files
                file1 = request.FILES.get('file1')
                file2 = request.FILES.get('file2')
                
                if not file1 or not file2:
                    form.add_error(None, "Both files are required for file comparison")
                    context = {
                        'form': form,
                        'comparison_result': None,
                        'similarity': None,
                        'history': history,
                        'page_title': 'Text & File Comparator',
                        'page_description': 'Compare texts and files to find differences'
                    }
                    return render(request, 'textcomparator/index.html', context)
                
                try:
                    # Read file contents (max 1MB per file)
                    if file1.size > 1048576 or file2.size > 1048576:
                        form.add_error(None, "File size must be less than 1MB")
                        context = {
                            'form': form,
                            'comparison_result': None,
                            'similarity': None,
                            'history': history,
                            'page_title': 'Text & File Comparator',
                            'page_description': 'Compare texts and files to find differences'
                        }
                        return render(request, 'textcomparator/index.html', context)
                    
                    text1 = file1.read().decode('utf-8', errors='replace')
                    text2 = file2.read().decode('utf-8', errors='replace')
                    file1_name = file1.name
                    file2_name = file2.name
                except Exception as e:
                    form.add_error(None, f"Error reading files: {str(e)}")
                    context = {
                        'form': form,
                        'comparison_result': None,
                        'similarity': None,
                        'history': history,
                        'page_title': 'Text & File Comparator',
                        'page_description': 'Compare texts and files to find differences'
                    }
                    return render(request, 'textcomparator/index.html', context)
            else:
                # Use text input
                text1 = form.cleaned_data.get('text1', '')
                text2 = form.cleaned_data.get('text2', '')
                file1_name = None
                file2_name = None
                
                if not text1 or not text2:
                    form.add_error(None, "Both text fields are required for text comparison")
                    context = {
                        'form': form,
                        'comparison_result': None,
                        'similarity': None,
                        'history': history,
                        'page_title': 'Text & File Comparator',
                        'page_description': 'Compare texts and files to find differences'
                    }
                    return render(request, 'textcomparator/index.html', context)
            
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
            
            # Build comparison result based on type
            if comparison_type == 'similarities_differences':
                comparison_result = {
                    'text1': text1,
                    'text2': text2,
                    'type': comparison_type,
                    'similarities': diff_result.get('similarities', []),
                    'removed': diff_result.get('removed', []),
                    'added': diff_result.get('added', []),
                    'differences': differences,
                    'similarity': round(similarity, 2)
                }
            else:
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


@require_http_methods(["POST"])
def download_comparison_results(request):
    """Download comparison results as a file (TXT or JSON)"""
    try:
        data = json.loads(request.body)
        file_format = data.get('format', 'txt')  # 'txt' or 'json'
        
        # Extract comparison data from request
        comparison_data = {
            'text1': data.get('text1', ''),
            'text2': data.get('text2', ''),
            'type': data.get('type', 'character'),
            'similarity': data.get('similarity', 0),
            'differences': data.get('differences', 0),
            'diff_output': data.get('diff_output', ''),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if file_format == 'json':
            # Generate JSON file
            content = json.dumps(comparison_data, indent=2, ensure_ascii=False)
            filename = f'comparison_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            content_type = 'application/json'
        else:
            # Generate TXT file
            content = f"""═══════════════════════════════════════════════════════════════
                    TEXT COMPARISON RESULTS
═══════════════════════════════════════════════════════════════

Generated: {comparison_data['timestamp']}
Comparison Type: {comparison_data['type'].upper()}
Similarity: {comparison_data['similarity']}%
Differences Found: {comparison_data['differences']}

───────────────────────────────────────────────────────────────
TEXT 1 (Preview - First 500 chars):
───────────────────────────────────────────────────────────────
{comparison_data['text1'][:500]}

───────────────────────────────────────────────────────────────
TEXT 2 (Preview - First 500 chars):
───────────────────────────────────────────────────────────────
{comparison_data['text2'][:500]}

───────────────────────────────────────────────────────────────
DETAILED DIFFERENCES:
───────────────────────────────────────────────────────────────
{comparison_data['diff_output']}

═══════════════════════════════════════════════════════════════
"""
            filename = f'comparison_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
            content_type = 'text/plain'
        
        response = HttpResponse(content, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
