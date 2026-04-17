from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
from collections import Counter
import csv
import io


def index(request):
    """Render the Duplicate Counter main page."""
    return render(request, 'duplicatecounter/index.html')


@require_http_methods(['POST'])
def count_duplicates(request):
    """Count duplicates and return results."""
    try:
        data = json.loads(request.body)
        text = data.get('text', '')
        sort_by = data.get('sort_by', 'count')  # count or line
        include_counts = data.get('include_counts', True)
        values_filter = data.get('values_filter', 'all')  # all or duplicates_only
        output_format = data.get('format', 'text')  # text, csv, tab
        
        if not text.strip():
            return JsonResponse({'error': 'Please enter some items'}, status=400)
        
        # Split by newlines and clean
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Count occurrences
        item_counts = Counter(lines)
        
        # Filter based on values_filter
        if values_filter == 'duplicates_only':
            item_counts = Counter({item: count for item, count in item_counts.items() if count > 1})
        
        # Sort based on sort_by
        if sort_by == 'count':
            sorted_items = sorted(item_counts.items(), key=lambda x: (-x[1], x[0]))
        else:  # sort by line (alphabetically)
            sorted_items = sorted(item_counts.items(), key=lambda x: x[0])
        
        # Format output
        if output_format == 'text':
            if include_counts:
                result = '\n'.join([f"{item} ({count})" for item, count in sorted_items])
                result_array = [{"item": item, "count": count} for item, count in sorted_items]
            else:
                result = '\n'.join([item for item, count in sorted_items])
                result_array = [{"item": item, "count": count} for item, count in sorted_items]
        
        elif output_format == 'csv':
            output = io.StringIO()
            if include_counts:
                writer = csv.writer(output)
                writer.writerow(['Item', 'Count'])
                for item, count in sorted_items:
                    writer.writerow([item, count])
            else:
                writer = csv.writer(output)
                writer.writerow(['Item'])
                for item, count in sorted_items:
                    writer.writerow([item])
            result = output.getvalue().strip()
            result_array = [{"item": item, "count": count} for item, count in sorted_items]
        
        elif output_format == 'tab':
            if include_counts:
                result = '\n'.join([f"{item}\t{count}" for item, count in sorted_items])
            else:
                result = '\n'.join([item for item, count in sorted_items])
            result_array = [{"item": item, "count": count} for item, count in sorted_items]
        
        else:
            result = '\n'.join([f"{item} ({count})" for item, count in sorted_items])
            result_array = [{"item": item, "count": count} for item, count in sorted_items]
        
        # Statistics
        total_items = len(lines)
        unique_items = len(item_counts)
        max_count = max(item_counts.values()) if item_counts else 0
        
        return JsonResponse({
            'result': result,
            'result_array': result_array,
            'stats': {
                'total_items': total_items,
                'unique_items': unique_items,
                'max_duplicates': max_count,
                'duplicates_count': sum(1 for count in item_counts.values() if count > 1)
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(['POST'])
def analyze_items(request):
    """Analyze items for detailed statistics."""
    try:
        data = json.loads(request.body)
        text = data.get('text', '')
        
        if not text.strip():
            return JsonResponse({'error': 'Please enter some items'}, status=400)
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        item_counts = Counter(lines)
        
        duplicates = {item: count for item, count in item_counts.items() if count > 1}
        unique_only = {item: count for item, count in item_counts.items() if count == 1}
        
        return JsonResponse({
            'total': len(lines),
            'unique': len(item_counts),
            'duplicates': len(duplicates),
            'unique_only_count': len(unique_only),
            'max_count': max(item_counts.values()) if item_counts else 0,
            'most_common': item_counts.most_common(5) if item_counts else []
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
